import cv2
import numpy as np
import tempfile
import os
from gtts import gTTS
from typing import Optional, Tuple, List
import logging
from config import Config

# Attempt to import MoviePy; provide a clear message if unavailable
try:
	from moviepy.editor import AudioFileClip, VideoFileClip
	MOVIEPY_AVAILABLE = True
except Exception as _moviepy_import_error:
	MOVIEPY_AVAILABLE = False
	MOVIEPY_IMPORT_ERROR = _moviepy_import_error

# Attempt to import imageio-ffmpeg for ffmpeg fallback
try:
	import imageio_ffmpeg
	IMAGEIO_FFMPEG_AVAILABLE = True
except Exception as _imageio_import_error:
	IMAGEIO_FFMPEG_AVAILABLE = False
	IMAGEIO_IMPORT_ERROR = _imageio_import_error

# Attempt to import mutagen for MP3 duration probing (when MoviePy is absent)
try:
	from mutagen.mp3 import MP3
	MUTAGEN_AVAILABLE = True
except Exception:
	MUTAGEN_AVAILABLE = False

import subprocess

# Attempt to import ElevenLabs TTS
try:
	from elevenlabs import generate as el_generate, save as el_save, set_api_key as el_set_key, voices as el_voices
	eleven_available = True
except Exception:
	eleven_available = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoGenerator:
	"""Handles video generation from text content"""
	
	def __init__(self):
		self.config = Config()
		# Load the default background image
		self.default_background = self._load_default_background()
	
	def _load_default_background(self) -> Optional[np.ndarray]:
		"""Load the default background image testbg.jpeg"""
		try:
			bg_path = "testbg.jpeg"
			if os.path.exists(bg_path):
				img = cv2.imread(bg_path)
				if img is not None:
					logger.info(f"Loaded default background image: {bg_path}")
					return img
				else:
					logger.warning(f"Failed to load default background image: {bg_path}")
			else:
				logger.warning(f"Default background image not found: {bg_path}")
		except Exception as e:
			logger.error(f"Error loading default background image: {e}")
		return None
	
	def set_default_background(self, image_path: str) -> bool:
		"""Set a new default background image"""
		try:
			if os.path.exists(image_path):
				img = cv2.imread(image_path)
				if img is not None:
					self.default_background = img
					logger.info(f"Set new default background image: {image_path}")
					return True
				else:
					logger.error(f"Failed to load image: {image_path}")
			else:
				logger.error(f"Image file not found: {image_path}")
		except Exception as e:
			logger.error(f"Error setting default background image: {e}")
		return False

	def _parse_explainer_script(self, script: str) -> list:
		"""Parse a structured script into slides.

		Expected format:
		### Slide X: Title
		- Bullet 1
		- Bullet 2
		...
		"""
		slides = []
		current = {"title": None, "bullets": []}
		for raw_line in script.splitlines():
			line = raw_line.strip()
			if not line:
				continue
			if line.startswith("### "):
				# start a new slide
				if current["title"] or current["bullets"]:
					slides.append(current)
				current = {"title": line.replace("###", "").strip(), "bullets": []}
			elif line.startswith("- "):
				current["bullets"].append(line[2:].strip())
			else:
				# append as a bullet if no marker
				current["bullets"].append(line)
		# push last
		if current["title"] or current["bullets"]:
			slides.append(current)
		return slides

	def _compose_slide_tts_text(self, slide: dict) -> str:
		parts = []
		if slide.get("title"):
			parts.append(slide["title"]) 
		for b in slide.get("bullets", []):
			parts.append(b)
		return ". ".join(parts)

	def _resize_and_crop(self, img: np.ndarray, width: int, height: int) -> np.ndarray:
		"""Resize to cover and center-crop to target size."""
		h, w = img.shape[:2]
		scale = max(width / float(w), height / float(h))
		resized = cv2.resize(img, (int(w * scale), int(h * scale)))
		rh, rw = resized.shape[:2]
		x1 = max(0, (rw - width) // 2)
		y1 = max(0, (rh - height) // 2)
		crop = resized[y1:y1 + height, x1:x1 + width]
		if crop.shape[0] != height or crop.shape[1] != width:
			padded = np.zeros((height, width, 3), dtype=np.uint8)
			padded[:crop.shape[0], :crop.shape[1]] = crop
			return padded
		return crop

	def _ken_burns_frame(self, base_img: np.ndarray, width: int, height: int, t: float, total: float) -> np.ndarray:
		"""Pan/zoom over time ensuring the image fully covers the frame (no corner padding)."""
		start_scale = 1.05
		end_scale = 1.15
		alpha = min(1.0, max(0.0, t / max(0.001, total)))
		# Compute scale so that the image always covers the output dimensions
		h, w = base_img.shape[:2]
		base_scale = max(width / float(max(1, w)), height / float(max(1, h)))
		cur_scale = base_scale * (start_scale + (end_scale - start_scale) * alpha)
		resized = cv2.resize(base_img, (int(w * cur_scale), int(h * cur_scale)))
		rh, rw = resized.shape[:2]
		# Pan from left-top to right-bottom
		x_offset = int(max(0, rw - width) * alpha)
		y_offset = int(max(0, rh - height) * alpha)
		x_offset = min(max(0, x_offset), max(0, rw - width))
		y_offset = min(max(0, y_offset), max(0, rh - height))
		crop = resized[y_offset:y_offset + height, x_offset:x_offset + width]
		# If rounding produced off-by-one sizes, fix by resizing to exact output size
		if crop.shape[0] != height or crop.shape[1] != width:
			crop = cv2.resize(crop, (width, height))
		return crop

	def _wrap_text_to_width(self, text: str, font_scale: float, thickness: int, max_width_px: int) -> list:
		"""Word-wrap text so each line fits within max_width_px for the given font."""
		words = text.replace("\n", " ").split()
		lines = []
		current = ""
		for w in words:
			candidate = (current + " " + w).strip() if current else w
			(text_size, _) = cv2.getTextSize(candidate, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
			if text_size[0] <= max_width_px:
				current = candidate
			else:
				if current:
					lines.append(current)
				current = w
		if current:
			lines.append(current)
		return lines

	def _sanitize_overlay_text(self, text: str) -> str:
		"""Sanitize for OpenCV font: keep ASCII, remove common punctuation that clutters overlays."""
		try:
			ascii_text = text.encode("ascii", errors="ignore").decode("ascii")
			for ch in [".", "?", ":", ";", "•", "–", "—"]:
				ascii_text = ascii_text.replace(ch, "")
			return ascii_text
		except Exception:
			return text

	def _draw_slide_text(self, frame: np.ndarray, title: str, bullets: list) -> np.ndarray:
		"""Overlay title and bullets on frame."""
		img = frame.copy()
		overlay = img.copy()
		cv2.rectangle(overlay, (30, 60), (img.shape[1] - 30, img.shape[0] - 60), (0, 0, 0), -1)
		img = cv2.addWeighted(overlay, 0.35, img, 0.65, 0)
		# Title
		if title:
			safe_title = self._sanitize_overlay_text(str(title))
			max_width = img.shape[1] - 120
			title_lines = self._wrap_text_to_width(safe_title, 1.1, 3, max_width)
			y_title = 120
			for tl in title_lines[:2]:
				cv2.putText(img, tl, (60, y_title), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3, lineType=cv2.LINE_AA)
				y_title += 46
		# Bullets
		y = 170
		for bullet in bullets:
			safe_bullet = self._sanitize_overlay_text(str(bullet))
			max_width = img.shape[1] - 120
			wrapped = self._wrap_text_to_width(safe_bullet, 0.8, 2, max_width)
			for line in wrapped:
				cv2.putText(img, f"- {line}", (60, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (240, 240, 240), 2, lineType=cv2.LINE_AA)
				y += 34
		return img

	def _draw_slide_text_styled(self, frame: np.ndarray, title: str, bullets: list, style: Optional[dict]) -> np.ndarray:
		"""Overlay title and bullets with optional style guidance."""
		if not style:
			return self._draw_slide_text(frame, title, bullets)
		img = frame.copy()
		overlay = img.copy()
		overlay_color = (0, 0, 0)
		if isinstance(style.get("overlay_color"), (list, tuple)) and len(style.get("overlay_color")) == 3:
			rgb = style.get("overlay_color")
			overlay_color = (int(rgb[2]), int(rgb[1]), int(rgb[0]))
		alpha = float(style.get("overlay_alpha", 0.35))
		cv2.rectangle(overlay, (30, 60), (img.shape[1] - 30, img.shape[0] - 60), overlay_color, -1)
		img = cv2.addWeighted(overlay, alpha, img, 1.0 - alpha, 0)
		text_color = (255, 255, 255)
		if isinstance(style.get("text_color"), (list, tuple)) and len(style.get("text_color")) == 3:
			rgb = style.get("text_color")
			text_color = (int(rgb[2]), int(rgb[1]), int(rgb[0]))
		title_scale = float(style.get("title_scale", 1.1))
		bullet_scale = float(style.get("bullet_scale", 0.8))
		# Title
		if title:
			safe_title = self._sanitize_overlay_text(str(title))
			max_width = img.shape[1] - 120
			title_lines = self._wrap_text_to_width(safe_title, title_scale, 3, max_width)
			y_title = 120
			for tl in title_lines[:2]:
				cv2.putText(img, tl, (60, y_title), cv2.FONT_HERSHEY_SIMPLEX, title_scale, text_color, 3, lineType=cv2.LINE_AA)
				y_title += int(42 * (title_scale / 1.1))
		# Bullets
		y = 170
		for bullet in bullets:
			safe_bullet = self._sanitize_overlay_text(str(bullet))
			max_width = img.shape[1] - 120
			wrapped = self._wrap_text_to_width(safe_bullet, bullet_scale, 2, max_width)
			for line in wrapped:
				cv2.putText(img, f"- {line}", (60, y), cv2.FONT_HERSHEY_SIMPLEX, bullet_scale, text_color, 2, lineType=cv2.LINE_AA)
				y += int(34 * (bullet_scale / 0.8))
		return img

	def extract_style_from_reference(self, reference_video_path: str, max_samples: int = 60) -> dict:
		"""Infer simple style cues (pacing, palette) from a reference MP4."""
		style = {
			"seconds_per_slide": 7.0,
			"overlay_alpha": 0.35,
			"overlay_color": (0, 0, 0),
			"text_color": (255, 255, 255),
			"title_scale": 1.1,
			"bullet_scale": 0.8,
		}
		try:
			cap = cv2.VideoCapture(reference_video_path)
			if not cap.isOpened():
				return style
			fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
			total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
			if total_frames <= 0:
				cap.release()
				return style
			duration_s = max(1.0, total_frames / float(fps))
			step = max(1, total_frames // max(1, min(max_samples, total_frames)))
			palette = []
			last_gray_small = None
			cut_count = 0
			for fidx in range(0, total_frames, step):
				cap.set(cv2.CAP_PROP_POS_FRAMES, fidx)
				ret, frame = cap.read()
				if not ret:
					continue
				small = cv2.resize(frame, (64, 64))
				Z = small.reshape((-1,3)).astype(np.float32)
				K = 3
				criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
				_, labels, centers = cv2.kmeans(Z, K, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
				counts = np.bincount(labels.flatten(), minlength=K)
				dominant_bgr = centers[np.argmax(counts)]
				rgb = (int(dominant_bgr[2]), int(dominant_bgr[1]), int(dominant_bgr[0]))
				palette.append(rgb)
				gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
				if last_gray_small is not None:
					diff = cv2.absdiff(gray, last_gray_small)
					mean_diff = float(np.mean(diff))
					if mean_diff > 20.0:
						cut_count += 1
				last_gray_small = gray
			cap.release()
			if cut_count >= 1:
				sps = duration_s / float(cut_count + 1)
				style["seconds_per_slide"] = float(max(4.0, min(15.0, sps)))
			if palette:
				med = np.median(np.array(palette), axis=0)
				style["overlay_color"] = (int(med[0]), int(med[1]), int(med[2]))
				brightness = 0.2126*med[0] + 0.7152*med[1] + 0.0722*med[2]
				style["overlay_alpha"] = 0.45 if brightness > 180 else 0.35
				style["text_color"] = (0, 0, 0) if brightness > 200 else (255, 255, 255)
			style["title_scale"] = 1.2 if self.config.DEFAULT_VIDEO_WIDTH >= 1280 else 1.0
			style["bullet_scale"] = 0.9 if self.config.DEFAULT_VIDEO_WIDTH >= 1280 else 0.8
			return style
		except Exception:
			return style

	def generate_slideshow_video_structured(
		self,
		structured: dict,
		image_paths: Optional[list] = None,
		output_path: str = "final_explanation_video.mp4",
		width: Optional[int] = None,
		height: Optional[int] = None,
		fps: Optional[int] = None,
		seconds_per_slide: float = 8.0,
		style: Optional[dict] = None,
		voice_gender: Optional[str] = None,
		voice_name: Optional[str] = None,
	) -> str:
		"""Render a slideshow using structured slides. Uses narration for TTS and bullets on-screen."""
		# convert to script-like for on-screen bullets, but TTS uses narration
		slides = structured.get("slides", []) if isinstance(structured, dict) else []
		if not slides:
			raise ValueError("Structured slides missing")
		# Prepare a pseudo-script to reuse frame rendering
		formatted = []
		for i, s in enumerate(slides, 1):
			title = s.get("title", f"Slide {i}")
			formatted.append(f"### {title}")
			for b in s.get("bullets", [])[:5]:
				formatted.append(f"- {b}")
		# Render per-slide frames and merge with per-slide narration
		width = width or self.config.DEFAULT_VIDEO_WIDTH
		height = height or self.config.DEFAULT_VIDEO_HEIGHT
		fps = fps or self.config.DEFAULT_FPS
		# load images (auto-fetch from structured.kb if none provided)
		loaded_images: List[Optional[np.ndarray]] = []
		if image_paths:
			for p in image_paths:
				try:
					img = cv2.imread(p)
					if img is None:
						loaded_images.append(None)
					else:
						loaded_images.append(self._resize_and_crop(img, width, height))
				except Exception:
					loaded_images.append(None)
		else:
			# Prefer local default background 'testbg.jpeg' if available
			try:
				proj_dir = os.path.dirname(os.path.abspath(__file__))
				default_bg = os.path.join(proj_dir, "testbg.jpeg")
				if os.path.exists(default_bg):
					img = cv2.imread(default_bg)
					if img is not None:
						loaded_images.append(self._resize_and_crop(img, width, height))
			except Exception:
				pass
			# Otherwise attempt to fetch images via URLs if present under key 'kb_images'
			if not loaded_images:
				kb_images = structured.get("kb_images") if isinstance(structured, dict) else None
				if isinstance(kb_images, list):
					for url in kb_images[:10]:
						try:
							import urllib.request
							resp = urllib.request.urlopen(url, timeout=10)
							data = resp.read()
							arr = np.frombuffer(data, np.uint8)
							img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
							if img is not None:
								loaded_images.append(self._resize_and_crop(img, width, height))
						except Exception:
							loaded_images.append(None)
		# iterate
		temp_silent_videos = []
		temp_audios = []
		temp_av_videos = []
		for idx, s in enumerate(slides):
			# narration text preferred; fallback to bullets join
			narr = s.get("narration") or ". ".join(s.get("bullets", []))
			narr_prefix = f"Slide {idx+1}. "
			narr_full = (narr_prefix + narr).strip()
			audio_path = self.text_to_speech(narr_full, voice_gender=voice_gender, voice_name=voice_name)
			temp_audios.append(audio_path)
			dur = None
			if MUTAGEN_AVAILABLE:
				try:
					meta = MP3(audio_path)
					dur = float(max(0.1, meta.info.length))
				except Exception:
					pass
			duration = max(seconds_per_slide, dur or seconds_per_slide)
			# build video
			temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
			temp_video_path = temp_video.name
			temp_video.close()
			fourcc = cv2.VideoWriter_fourcc(*"mp4v")
			writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
			frames = int(duration * fps)
			bg_img = loaded_images[idx % len(loaded_images)] if loaded_images else None
			for f in range(frames):
				t = f / float(fps)
				if bg_img is not None:
					frame = self._ken_burns_frame(bg_img, width, height, t, duration)
				elif self.default_background is not None:
					frame = self._ken_burns_frame(self.default_background, width, height, t, duration)
				else:
					frame = np.zeros((height, width, 3), dtype=np.uint8)
					frame[:] = (20, 30, 45)
				frame = self._draw_slide_text(frame, s.get("title", ""), s.get("bullets", []))
				if t < 1.0:
					alpha = max(0.0, min(1.0, t / 1.0))
					frame = (frame.astype(np.float32) * alpha).astype(np.uint8)
				writer.write(frame)
			writer.release()
			temp_silent_videos.append(temp_video_path)
			# merge audio
			if IMAGEIO_FFMPEG_AVAILABLE:
				ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
				av_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
				av_out_path = av_out.name
				av_out.close()
				cmd = [
					ffmpeg_exe, "-y",
					"-i", temp_video_path,
					"-i", audio_path,
					"-filter_complex", f"[1:a]apad[aout]",
					"-map", "0:v",
					"-map", "[aout]",
					"-t", str(duration),
					"-c:v", "libx264",
					"-preset", "veryfast",
					"-c:a", "aac",
					av_out_path,
				]
				subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				temp_av_videos.append(av_out_path)
			else:
				raise RuntimeError("FFmpeg (imageio-ffmpeg) not available for structured slideshow generation.")
		# concatenate
		ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
		list_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
		list_path = list_file.name
		list_file.close()
		with open(list_path, "w") as f:
			for p in temp_av_videos:
				f.write(f"file '{p}'\n")
		concat_cmd = [
			ffmpeg_exe, "-y",
			"-f", "concat", "-safe", "0",
			"-i", list_path,
			"-c:v", "libx264",
			"-c:a", "aac",
			"-movflags", "+faststart",
			output_path,
		]
		subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		for p in temp_silent_videos + temp_audios + temp_av_videos:
			try:
				if os.path.exists(p):
					os.unlink(p)
			except Exception:
				pass
		try:
			os.unlink(list_path)
		except Exception:
			pass
		logger.info(f"Structured slideshow video generated: {output_path}")
		return output_path
	
	def text_to_speech(self, text: str, output_path: Optional[str] = None, voice_gender: Optional[str] = None, voice_name: Optional[str] = None) -> str:
		"""
		Convert text to speech and save as audio file
		
		Args:
			text: Text to convert to speech
			output_path: Optional path to save audio file
			
		Returns:
			Path to the generated audio file
		"""
		try:
			if output_path is None:
				# Create temporary file
				temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
				output_path = temp_file.name
				temp_file.close()
			# Prefer ElevenLabs if API key is available
			if eleven_available and self.config.ELEVENLABS_API_KEY:
				try:
					el_set_key(self.config.ELEVENLABS_API_KEY)
					# choose a voice
					voice_id = None
					if voice_name:
						voice_id = voice_name
					elif voice_gender:
						# naive mapping by gender keywords; users can provide exact voice name for precision
						preferred = 'Rachel' if voice_gender.lower().startswith('f') else 'Adam'
						voice_id = preferred
					else:
						voice_id = 'Adam'
					audio_bytes = el_generate(text=text, voice=voice_id, model="eleven_monolingual_v1")
					el_save(audio_bytes, output_path)
					logger.info(f"Audio generated via ElevenLabs: {output_path}")
					return output_path
				except Exception as _e:
					logger.warning(f"ElevenLabs TTS failed, falling back to gTTS: {_e}")
			# gTTS fallback
			tts = gTTS(text=text, lang=self.config.TTS_LANGUAGE, slow=self.config.TTS_SLOW)
			tts.save(output_path)
			logger.info(f"Audio generated successfully: {output_path}")
			return output_path
			
		except Exception as e:
			logger.error(f"Error in text-to-speech conversion: {e}")
			raise
	
	def _wrap_text_fixed_width(self, text: str, max_chars_per_line: int = 40) -> list:
		"""Simple fixed-width wrapper for drawing with cv2."""
		lines = []
		current = ""
		for ch in text:
			if ch == "\n":
				lines.append(current)
				current = ""
				continue
			current += ch
			if len(current) >= max_chars_per_line:
				lines.append(current)
				current = ""
		if current:
			lines.append(current)
		return lines
	
	def _draw_typewriter_frame(self, visible_text: str, width: int, height: int, caret_visible: bool) -> np.ndarray:
		"""Render a frame showing the visible portion of text with a blinking caret."""
		# Use default background if available, otherwise create a solid color frame
		if self.default_background is not None:
			frame = self._resize_and_crop(self.default_background, width, height)
		else:
		   frame = np.zeros((height, width, 3), dtype=np.uint8)
		   frame[:] = (20, 30, 45)
		
		lines = self._wrap_text_fixed_width(visible_text, max_chars_per_line=40)
		
		# Add caret at the end if typing not finished
		if caret_visible:
			if lines:
				lines[-1] = lines[-1] + "|"
			else:
				lines = ["|"]
		
		# Add semi-transparent overlay for better text readability
		overlay = frame.copy()
		cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
		frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
		
		y_start = 200
		line_height = 50
		for i, line in enumerate(lines):
			y = y_start + i * line_height
			cv2.putText(
				frame,
				line,
				(50, y),
				cv2.FONT_HERSHEY_SIMPLEX,
				1.2,
				(255, 255, 255),
				3,
				lineType=cv2.LINE_AA
			)
		return frame
	
	def generate_video(
		self, 
		text: str, 
		duration: int, 
		output_path: str = "final_explanation_video.mp4",
		width: Optional[int] = None,
		height: Optional[int] = None,
		fps: Optional[int] = None
	) -> str:
		"""
		Generate video from text with typewriter animation, synced to TTS audio
		
		Args:
			text: Text content for the video
			duration: Target video duration in seconds (min will be audio length)
			output_path: Path to save the final video (with audio)
			width: Video width (optional)
			height: Video height (optional)
			fps: Frames per second (optional)
			
		Returns:
			Path to the generated video file
		"""
		try:
			# Use config defaults if not specified
			width = width or self.config.DEFAULT_VIDEO_WIDTH
			height = height or self.config.DEFAULT_VIDEO_HEIGHT
			fps = fps or self.config.DEFAULT_FPS
			
			# Validate and clamp duration
			target_duration = max(1, int(duration))
			if target_duration > self.config.MAX_VIDEO_DURATION:
				target_duration = self.config.MAX_VIDEO_DURATION
			
			# 1) Generate audio
			audio_path = self.text_to_speech(text)
			
			# 2) Determine audio duration
			audio_duration = None
			if MOVIEPY_AVAILABLE:
				audio_clip = AudioFileClip(audio_path)
				audio_duration = float(max(0.1, audio_clip.duration))
			elif MUTAGEN_AVAILABLE:
				try:
					meta = MP3(audio_path)
					audio_duration = float(max(0.1, meta.info.length))
				except Exception:
					audio_duration = None
			
			if audio_duration is None:
				# Fallback: use target duration if probing not possible
				audio_duration = float(target_duration)
			
			# 3) Decide final duration and total frames
			final_duration = int(np.ceil(max(target_duration, audio_duration)))
			total_frames = int(final_duration * fps)
			
			# Typewriter timing: characters per second to finish at audio end
			total_chars = max(1, len(text))
			chars_per_second = total_chars / max(0.1, audio_duration)
			
			# 4) Create temp video without audio with animated frames
			temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
			temp_video_path = temp_video.name
			temp_video.close()
			
			fourcc = cv2.VideoWriter_fourcc(*"mp4v")
			video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
			
			for frame_index in range(total_frames):
				t = frame_index / float(fps)
				# Number of chars to reveal at time t
				num_chars = int(min(total_chars, round(chars_per_second * t)))
				visible_text = text[:num_chars]
				caret_visible = (frame_index // int(max(1, fps/2))) % 2 == 0 and num_chars < total_chars
				frame = self._draw_typewriter_frame(visible_text, width, height, caret_visible)
				video_writer.write(frame)
			
			video_writer.release()
			
			# 5) Merge audio with the generated video
			if MOVIEPY_AVAILABLE:
				video_clip = VideoFileClip(temp_video_path)
				video_clip = video_clip.set_audio(audio_clip)
				# Duration should cover both
				video_clip = video_clip.set_duration(max(video_clip.duration, audio_duration))
				video_clip.write_videofile(
					output_path,
					fps=fps,
					codec="libx264",
					audio_codec="aac",
					verbose=False,
					logger=None
				)
				video_clip.close()
				audio_clip.close()
			else:
				if not IMAGEIO_FFMPEG_AVAILABLE:
					raise RuntimeError(
						"MoviePy not installed and ffmpeg fallback unavailable. Install either moviepy or imageio-ffmpeg. "
						f"Import error: {IMAGEIO_IMPORT_ERROR}"
					)
				ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
				cmd = [
					ffmpeg_exe,
					"-y",
					"-i", temp_video_path,
					"-i", audio_path,
					"-c:v", "libx264",
					"-preset", "veryfast",
					"-c:a", "aac",
					"-shortest",
					output_path,
				]
				subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			
			# Cleanup resources
			if os.path.exists(temp_video_path):
				os.unlink(temp_video_path)
			if os.path.exists(audio_path):
				os.unlink(audio_path)
			
			logger.info(f"Video generated successfully with audio: {output_path}")
			return output_path
			
		except Exception as e:
			logger.error(f"Error in video generation: {e}")
			raise

	def generate_slideshow_video(
		self,
		script: str,
		image_paths: Optional[list] = None,
		output_path: str = "final_explanation_video.mp4",
		width: Optional[int] = None,
		height: Optional[int] = None,
		fps: Optional[int] = None,
		seconds_per_slide: float = 7.0,
		style: Optional[dict] = None,
	) -> str:
		"""Generate a slide-based explainer video from a structured script with optional images.

		If MoviePy is unavailable, attempt to import it now and raise a helpful error if that fails.
		"""
		# use config defaults
		width = width or self.config.DEFAULT_VIDEO_WIDTH
		height = height or self.config.DEFAULT_VIDEO_HEIGHT
		fps = fps or self.config.DEFAULT_FPS
		# parse slides
		slides = self._parse_explainer_script(script)
		if not slides:
			raise ValueError("No slides detected in script. Ensure headings start with '###'.")
		# load images
		loaded_images = []
		if image_paths:
			for p in image_paths:
				try:
					img = cv2.imread(p)
					if img is None:
						loaded_images.append(None)
					else:
						loaded_images.append(self._resize_and_crop(img, width, height))
				except Exception:
					loaded_images.append(None)
		else:
			# Prefer local default background 'testbg.jpeg' if available
			try:
				proj_dir = os.path.dirname(os.path.abspath(__file__))
				default_bg = os.path.join(proj_dir, "testbg.jpeg")
				if os.path.exists(default_bg):
					img = cv2.imread(default_bg)
					if img is not None:
						loaded_images.append(self._resize_and_crop(img, width, height))
			except Exception:
				pass
		# build per-slide videos and merge audio with ffmpeg if MoviePy not present
		temp_silent_videos = []
		temp_audios = []
		temp_av_videos = []
		for idx, slide in enumerate(slides):
			# audio
			audio_text = self._compose_slide_tts_text(slide)
			# narration text preferred; fallback to bullets join; ensure variation to avoid repetition
			narr = slide.get("narration") or ". ".join(slide.get("bullets", []))
			# add slide-specific prefix to reduce repetition artifacts in TTS prosody
			narr_prefix = f"Slide {idx+1}. "
			narr_full = (narr_prefix + narr).strip()
			audio_path = self.text_to_speech(narr_full)
			temp_audios.append(audio_path)
			# approximate duration using mutagen if available
			audio_duration = None
			if MUTAGEN_AVAILABLE:
				try:
					meta = MP3(audio_path)
					audio_duration = float(max(0.1, meta.info.length))
				except Exception:
					pass
			duration = max(seconds_per_slide, audio_duration or seconds_per_slide)
			# video frames
			temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
			temp_video_path = temp_video.name
			temp_video.close()
			fourcc = cv2.VideoWriter_fourcc(*"mp4v")
			writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
			frames = int(duration * fps)
			bg_img = None
			if loaded_images:
				bg_img = loaded_images[idx % len(loaded_images)] if loaded_images[idx % len(loaded_images)] is not None else None
			for f in range(frames):
				t = f / float(fps)
				if bg_img is not None:
					frame = self._ken_burns_frame(bg_img, width, height, t, duration)
				elif self.default_background is not None:
					frame = self._ken_burns_frame(self.default_background, width, height, t, duration)
				else:
					frame = np.zeros((height, width, 3), dtype=np.uint8)
					frame[:] = (20, 30, 45)
				frame = self._draw_slide_text_styled(frame, slide.get("title", ""), slide.get("bullets", []), style)
				if t < 1.0:
					alpha = max(0.0, min(1.0, t / 1.0))
					frame = (frame.astype(np.float32) * alpha).astype(np.uint8)
				writer.write(frame)
			writer.release()
			temp_silent_videos.append(temp_video_path)
			# merge audio + video via ffmpeg
			if IMAGEIO_FFMPEG_AVAILABLE:
				ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
				av_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
				av_out_path = av_out.name
				av_out.close()
				cmd = [
					ffmpeg_exe, "-y",
					"-i", temp_video_path,
					"-i", audio_path,
					"-c:v", "libx264",
					"-preset", "veryfast",
					"-c:a", "aac",
					"-shortest",
					av_out_path,
				]
				subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				temp_av_videos.append(av_out_path)
			else:
				raise RuntimeError("FFmpeg (imageio-ffmpeg) not available for slideshow generation.")
		# concatenate all av clips
		ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
		list_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
		list_path = list_file.name
		list_file.close()
		with open(list_path, "w") as f:
			for p in temp_av_videos:
				f.write(f"file '{p}'\n")
		concat_cmd = [
			ffmpeg_exe, "-y",
			"-f", "concat", "-safe", "0",
			"-i", list_path,
			"-c:v", "libx264",
			"-c:a", "aac",
			"-movflags", "+faststart",
			output_path,
		]
		subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		# cleanup temps
		for p in temp_silent_videos + temp_audios + temp_av_videos:
			try:
				if os.path.exists(p):
					os.unlink(p)
			except Exception:
				pass
		try:
			os.unlink(list_path)
		except Exception:
			pass
		logger.info(f"Slideshow video generated: {output_path}")
		return output_path
	
	def cleanup_temp_files(self, file_paths: list):
		"""Clean up temporary files"""
		for file_path in file_paths:
			try:
				if os.path.exists(file_path):
					os.unlink(file_path)
					logger.info(f"Cleaned up temporary file: {file_path}")
			except Exception as e:
				logger.warning(f"Failed to cleanup file {file_path}: {e}") 