import cv2
import numpy as np
import tempfile
import os
from gtts import gTTS
from typing import Optional, Tuple, List, Dict
import logging
from config import Config
import requests
import json
from PIL import Image
import io

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
	"""Handles video generation from text content with enhanced features"""
	
	def __init__(self):
		self.config = Config()
		# Load the default background image
		self.default_background = self._load_default_background()
		# Cache for topic-related backgrounds
		self.topic_backgrounds = {}
	
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
	
	def _get_topic_background(self, topic: str) -> Optional[np.ndarray]:
		"""Get a topic-related background image from Unsplash"""
		try:
			if topic in self.topic_backgrounds:
				return self.topic_backgrounds[topic]
			
			# Search for topic-related images on Unsplash
			search_query = topic.replace(" ", "+").lower()
			url = f"https://api.unsplash.com/search/photos?query={search_query}&orientation=landscape&per_page=1"
			
			# For demo purposes, we'll use a fallback approach
			# In production, you'd need an Unsplash API key
			fallback_images = {
				"technology": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1280&h=720&fit=crop",
				"science": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1280&h=720&fit=crop",
				"education": "https://images.unsplash.com/photo-1523050854058-8df90110c9c1?w=1280&h=720&fit=crop",
				"business": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1280&h=720&fit=crop",
				"health": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=1280&h=720&fit=crop",
				"art": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=1280&h=720&fit=crop",
				"nature": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1280&h=720&fit=crop",
				"space": "https://images.unsplash.com/photo-1446776811953-b23d0bd8436c?w=1280&h=720&fit=crop"
			}
			
			# Find the best matching fallback image
			best_match = None
			best_score = 0
			for key, image_url in fallback_images.items():
				score = self._calculate_topic_similarity(topic, key)
				if score > best_score:
					best_score = score
					best_match = image_url
			
			if best_match:
				# Download and process the image
				response = requests.get(best_match, timeout=10)
				if response.status_code == 200:
					# Convert PIL image to OpenCV format
					pil_image = Image.open(io.BytesIO(response.content))
					opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
					
					# Cache the result
					self.topic_backgrounds[topic] = opencv_image
					logger.info(f"Loaded topic-related background for: {topic}")
					return opencv_image
			
		except Exception as e:
			logger.warning(f"Failed to get topic background for {topic}: {e}")
		
		return None
	
	def _calculate_topic_similarity(self, topic: str, category: str) -> float:
		"""Calculate similarity between topic and category for background selection"""
		topic_words = set(topic.lower().split())
		category_words = set(category.lower().split())
		
		# Simple word overlap similarity
		if not topic_words or not category_words:
			return 0.0
		
		intersection = len(topic_words.intersection(category_words))
		union = len(topic_words.union(category_words))
		
		return intersection / union if union > 0 else 0.0
	
	def _improve_content_flow(self, text: str) -> str:
		"""Improve content flow to avoid repetition and improve TTS quality"""
		# Remove excessive punctuation that can cause TTS breaks
		text = text.replace("...", ".")
		text = text.replace("..", ".")
		text = text.replace("--", "-")
		
		# Add natural pauses for better TTS flow
		sentences = text.split(".")
		improved_sentences = []
		
		for sentence in sentences:
			sentence = sentence.strip()
			if sentence:
				# Add natural pauses after key phrases
				sentence = sentence.replace(" for example", ". For example")
				sentence = sentence.replace(" however", ". However")
				sentence = sentence.replace(" therefore", ". Therefore")
				sentence = sentence.replace(" in addition", ". In addition")
				sentence = sentence.replace(" on the other hand", ". On the other hand")
				
				improved_sentences.append(sentence)
		
		# Join with proper spacing
		result = ". ".join(improved_sentences)
		
		# Ensure proper capitalization
		if result:
			result = result[0].upper() + result[1:]
		
		return result
	
	def _create_enhanced_slide_content(self, slide: Dict) -> str:
		"""Create enhanced slide content with better flow and structure - NotebookLM style"""
		title = slide.get("title", "")
		bullets = slide.get("bullets", [])
		narration = slide.get("narration", "")
		
		# For NotebookLM style, create flowing explanations, not bullet reading
		if narration:
			# Use existing narration but clean it up
			content = narration
		else:
			# Create flowing explanation from bullets (not reading them)
			bullet_texts = []
			for i, bullet in enumerate(bullets):
				if i == 0:
					bullet_texts.append(f"Let me explain {bullet.lower()}")
				elif i == len(bullets) - 1:
					bullet_texts.append(f"Finally, {bullet.lower()}")
				else:
					bullet_texts.append(f"Next, {bullet.lower()}")
			
			content = ". ".join(bullet_texts)
		
		# Improve content flow for NotebookLM style
		content = self._improve_content_flow(content)
		
		return content
	
	def _draw_enhanced_slide_text(self, frame: np.ndarray, title: str, bullets: list, topic: str = "") -> np.ndarray:
		"""Enhanced text overlay with better positioning and styling"""
		img = frame.copy()
		
		# Create a more sophisticated overlay
		overlay = img.copy()
		
		# Gradient overlay for better text readability
		height, width = img.shape[:2]
		for y in range(height):
			alpha = 0.3 + (0.2 * y / height)  # Gradient from top to bottom
			overlay[y, :] = img[y, :] * (1 - alpha) + np.array([0, 0, 0]) * alpha
		
		img = overlay.astype(np.uint8)
		
		# Add topic indicator if available
		if topic:
			topic_bg = np.zeros((60, width, 3), dtype=np.uint8)
			topic_bg[:] = (50, 100, 200)  # Blue background
			img[20:80, :] = cv2.addWeighted(img[20:80, :], 0.3, topic_bg, 0.7, 0)
			
			# Topic text
			cv2.putText(img, f"Topic: {topic}", (30, 55), 
						cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, 
						lineType=cv2.LINE_AA)
		
		# Title with enhanced styling
		if title:
			safe_title = self._sanitize_overlay_text(str(title))
			max_width = width - 120
			title_lines = self._wrap_text_to_width(safe_title, 1.3, 3, max_width)
			
			# Center the title
			y_title = 140
			for tl in title_lines[:2]:
				text_size = cv2.getTextSize(tl, cv2.FONT_HERSHEY_SIMPLEX, 1.3, 3)[0]
				x_center = (width - text_size[0]) // 2
				x_center = max(60, min(x_center, width - text_size[0] - 60))
				
				# Title background for better readability
				cv2.rectangle(img, (x_center - 10, y_title - 35), 
							(x_center + text_size[0] + 10, y_title + 10), 
							(0, 0, 0), -1)
				cv2.rectangle(img, (x_center - 10, y_title - 35), 
							(x_center + text_size[0] + 10, y_title + 10), 
							(255, 255, 255), 2)
				
				cv2.putText(img, tl, (x_center, y_title), 
							cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3, 
							lineType=cv2.LINE_AA)
				y_title += 50
		
		# Bullets with better positioning
		y_start = 220
		line_height = 40
		
		for i, bullet in enumerate(bullets):
			safe_bullet = self._sanitize_overlay_text(str(bullet))
			max_width = width - 120
			wrapped = self._wrap_text_to_width(safe_bullet, 0.9, 2, max_width)
			
			for j, line in enumerate(wrapped):
				y = y_start + i * line_height + j * 30
				
				# Bullet background
				text_size = cv2.getTextSize(f"• {line}", cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
				cv2.rectangle(img, (50, y - 20), (60 + text_size[0], y + 10), 
							(0, 0, 0), -1)
				
				cv2.putText(img, f"• {line}", (60, y), 
							cv2.FONT_HERSHEY_SIMPLEX, 0.9, (240, 240, 240), 2, 
							lineType=cv2.LINE_AA)
		
		return img

	def _draw_clean_slide_text(self, frame: np.ndarray, title: str, bullets: list, topic: str = "", narration: str = "") -> np.ndarray:
		"""Clean, NotebookLM-style text overlay with minimal content and clear focus"""
		img = frame.copy()
		
		# Create a subtle overlay for better readability
		overlay = img.copy()
		height, width = img.shape[:2]
		
		# Subtle gradient overlay (lighter than before)
		for y in range(height):
			alpha = 0.15 + (0.1 * y / height)  # Much lighter overlay
			overlay[y, :] = img[y, :] * (1 - alpha) + np.array([0, 0, 0]) * alpha
		
		img = overlay.astype(np.uint8)
		
		# Add topic indicator at top (subtle)
		if topic:
			topic_bg = np.zeros((50, width, 3), dtype=np.uint8)
			topic_bg[:] = (40, 80, 160)  # Subtle blue
			img[20:70, :] = cv2.addWeighted(img[20:70, :], 0.8, topic_bg, 0.2, 0)
			
			# Topic text (smaller, subtle)
			cv2.putText(img, f"Topic: {topic}", (30, 45), 
						cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, 
						lineType=cv2.LINE_AA)
		
		# Title - clean and centered (main focus)
		if title:
			safe_title = self._sanitize_overlay_text(str(title))
			max_width = width - 100
			title_lines = self._wrap_text_to_width(safe_title, 1.5, 2, max_width)
			
			# Center the title prominently
			y_title = 150
			for tl in title_lines[:2]:
				text_size = cv2.getTextSize(tl, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
				x_center = (width - text_size[0]) // 2
				x_center = max(50, min(x_center, width - text_size[0] - 50))
				
				# Clean title background (minimal)
				cv2.rectangle(img, (x_center - 15, y_title - 40), 
							(x_center + text_size[0] + 15, y_title + 15), 
							(0, 0, 0), -1)
				cv2.rectangle(img, (x_center - 15, y_title - 40), 
							(x_center + text_size[0] + 15, y_title + 15), 
							(255, 255, 255), 1)
				
				cv2.putText(img, tl, (x_center, y_title), 
							cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, 
							lineType=cv2.LINE_AA)
				y_title += 60
		
		# Key points - minimal, clean (only 2-3 main points)
		key_points = bullets[:3]  # Limit to 3 key points
		y_start = 280
		line_height = 50
		
		for i, point in enumerate(key_points):
			safe_point = self._sanitize_overlay_text(str(point))
			max_width = width - 100
			wrapped = self._wrap_text_to_width(safe_point, 1.0, 1, max_width)
			
			for j, line in enumerate(wrapped):
				y = y_start + i * line_height + j * 35
				
				# Clean bullet background (minimal)
				text_size = cv2.getTextSize(f"• {line}", cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)[0]
				cv2.rectangle(img, (60, y - 15), (70 + text_size[0], y + 10), 
							(0, 0, 0), -1)
				
				cv2.putText(img, f"• {line}", (70, y), 
							cv2.FONT_HERSHEY_SIMPLEX, 1.0, (240, 240, 240), 1, 
							lineType=cv2.LINE_AA)
		
		# Add narration content - THIS IS THE KEY FIX!
		# Get narration from the slide data
		narration = getattr(self, '_current_slide_narration', '')
		if narration:
			# Display narration content below key points
			y_narration = y_start + len(key_points) * line_height + 80
			max_width = width - 120
			
			# Split narration into readable chunks
			words = narration.split()
			lines = []
			current_line = ""
			
			for word in words:
				test_line = current_line + " " + word if current_line else word
				if len(test_line) * 12 <= max_width:  # Approximate character width
					current_line = test_line
				else:
					if current_line:
						lines.append(current_line)
					current_line = word
			
			if current_line:
				lines.append(current_line)
			
			# Display narration lines
			for i, line in enumerate(lines[:6]):  # Limit to 6 lines
				y = y_narration + i * 30
				
				# Clean background for narration
				text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 1)[0]
				cv2.rectangle(img, (60, y - 10), (70 + text_size[0], y + 15), 
							(0, 0, 0), -1)
				
				cv2.putText(img, line, (70, y), 
							cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1, 
							lineType=cv2.LINE_AA)
		
		return img

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
		"""Create improved TTS text that flows better and avoids repetition"""
		return self._create_enhanced_slide_content(slide)

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
		desired_total_seconds: Optional[float] = None,
		style: Optional[dict] = None,
		voice_gender: Optional[str] = None,
		voice_name: Optional[str] = None,
		topic: Optional[str] = None,
	) -> str:
		"""Render a slideshow using structured slides. Uses narration for TTS and bullets on-screen."""
		# convert to script-like for on-screen bullets, but TTS uses narration
		slides = structured.get("slides", []) if isinstance(structured, dict) else []
		if not slides:
			raise ValueError("Structured slides missing")
		
		# Extract topic from structured data if not provided
		if not topic and isinstance(structured, dict):
			topic = structured.get("topic", "")
			if not topic and slides:
				# Try to extract from first slide title
				first_title = slides[0].get("title", "")
				if ":" in first_title:
					topic = first_title.split(":")[-1].strip()
				else:
					topic = first_title
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
		# Use topic-related backgrounds only (no custom images)
		loaded_images = []
		if topic:
			topic_bg = self._get_topic_background(topic)
			if topic_bg is not None:
				loaded_images.append(self._resize_and_crop(topic_bg, width, height))
		
		# Fallback to default background if no topic background
		if not loaded_images:
			try:
				proj_dir = os.path.dirname(os.path.abspath(__file__))
				default_bg = os.path.join(proj_dir, "testbg.jpeg")
				if os.path.exists(default_bg):
					img = cv2.imread(default_bg)
					if img is not None:
						loaded_images.append(self._resize_and_crop(img, width, height))
			except Exception:
				pass
		# iterate
		temp_silent_videos = []
		temp_audios = []
		temp_av_videos = []
		# First synthesize audio for each slide without saying slide numbers
		audio_durations = []
		for idx, s in enumerate(slides):
			# Use enhanced content flow for better TTS
			slide_content = self._create_enhanced_slide_content(s)
			audio_path = self.text_to_speech(slide_content, voice_gender=voice_gender, voice_name=voice_name)
			temp_audios.append(audio_path)
			dur = None
			if MUTAGEN_AVAILABLE:
				try:
					meta = MP3(audio_path)
					dur = float(max(0.1, meta.info.length))
				except Exception:
					pass
			audio_durations.append(float(dur or seconds_per_slide))
		# Choose durations to target 4-10 minutes total
		num_slides = max(1, len(slides))
		if desired_total_seconds is None:
			base_total = sum(max(6.0, d + 1.0) for d in audio_durations)
			desired_total = max(240.0, min(600.0, base_total))
		else:
			desired_total = max(240.0, min(600.0, float(desired_total_seconds)))
		median_audio = sorted(audio_durations)[len(audio_durations)//2] if audio_durations else seconds_per_slide
		uniform_seconds_per_slide = max(median_audio + 0.5, desired_total / float(num_slides))
		# Now render each slide using the decided duration
		for idx, s in enumerate(slides):
			duration = max(uniform_seconds_per_slide, audio_durations[idx])
			# build video
			temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
			temp_video_path = temp_video.name
			temp_video.close()
			fourcc = cv2.VideoWriter_fourcc(*"mp4v")
			writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
			frames = int(duration * fps)
			# Get topic-related background if available
			topic_bg = self._get_topic_background(topic) if topic else None
			bg_img = loaded_images[idx % len(loaded_images)] if loaded_images else topic_bg
			
			for f in range(frames):
				t = f / float(fps)
				if bg_img is not None:
					frame = self._ken_burns_frame(bg_img, width, height, t, duration)
				elif self.default_background is not None:
					frame = self._ken_burns_frame(self.default_background, width, height, t, duration)
				else:
					frame = np.zeros((height, width, 3), dtype=np.uint8)
					frame[:] = (20, 30, 45)
				
				# Use clean, NotebookLM-style text rendering
				# Set current slide narration for display
				self._current_slide_narration = s.get("narration", "")
				frame = self._draw_clean_slide_text(frame, s.get("title", ""), s.get("bullets", []), topic)
				
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
					"-i", temp_audios[idx],
					"-filter_complex", f"[1:a]apad[aout]",
					"-map", "0:v",
					"-map", "[aout]",
					"-t", str(duration),
					"-c:v", "libx264",
					"-preset", "veryfast",
					"-c:a", "aac",
					av_out_path,
				]
				result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
				if result.returncode == 0:
					temp_av_videos.append(av_out_path)
					logger.info(f"Audio merged successfully for slide {idx + 1}")
				else:
					logger.error(f"Failed to merge audio for slide {idx + 1}: {result.stderr}")
					# Fallback: use video without audio
					temp_av_videos.append(temp_video_path)
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
		result = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=120)
		if result.returncode != 0:
			logger.error(f"Final video concatenation failed: {result.stderr}")
			raise RuntimeError(f"Failed to create final video: {result.stderr}")
		logger.info("Final video concatenation successful")
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
					# choose a more human-sounding default voice
					voice_id = None
					if voice_name:
						voice_id = voice_name
					elif voice_gender:
						# naive mapping by gender keywords; users can provide exact voice name for precision
						preferred = 'Adam' if voice_gender.lower().startswith('m') else 'Rachel'
						voice_id = preferred
					else:
						voice_id = 'Adam'
					audio_bytes = el_generate(text=text, voice=voice_id, model="eleven_monolingual_v1")
					el_save(audio_bytes, output_path)
					logger.info(f"Audio generated via ElevenLabs: {output_path}")
					return output_path
				except Exception as _e:
					logger.warning(f"ElevenLabs TTS failed, falling back to gTTS: {_e}")
			# gTTS fallback with slightly slower pace for naturalness
			tts = gTTS(text=text, lang=self.config.TTS_LANGUAGE, slow=True if (voice_gender and voice_gender.lower().startswith('n')) else self.config.TTS_SLOW)
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
	
	def _draw_typewriter_frame(self, visible_text: str, width: int, height: int, caret_visible: bool, topic: str = None) -> np.ndarray:
		"""Render a frame showing the visible portion of text with a blinking caret."""
		# Use topic-related background if available, then default background
		if topic and hasattr(self, '_current_topic_background') and self._current_topic_background is not None:
			frame = self._resize_and_crop(self._current_topic_background, width, height)
		elif self.default_background is not None:
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
		fps: Optional[int] = None,
		topic: Optional[str] = None
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
			
			# 1) Generate audio with improved content flow
			improved_text = self._improve_content_flow(text)
			audio_path = self.text_to_speech(improved_text)
			
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
			total_chars = max(1, len(improved_text))
			chars_per_second = total_chars / max(0.1, audio_duration)
			
			# 4) Get topic-related background if available
			if topic:
				self._current_topic_background = self._get_topic_background(topic)
			
			# 5) Create temp video without audio with animated frames
			temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
			temp_video_path = temp_video.name
			temp_video.close()
			
			fourcc = cv2.VideoWriter_fourcc(*"mp4v")
			video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
			
			for frame_index in range(total_frames):
				t = frame_index / float(fps)
				# Number of chars to reveal at time t
				num_chars = int(min(total_chars, round(chars_per_second * t)))
				visible_text = improved_text[:num_chars]
				caret_visible = (frame_index // int(max(1, fps/2))) % 2 == 0 and num_chars < total_chars
				frame = self._draw_typewriter_frame(visible_text, width, height, caret_visible, topic)
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
		
		# Extract topic from first slide title for background selection
		topic = ""
		if slides and slides[0].get("title"):
			topic = slides[0]["title"].split(":")[-1].strip() if ":" in slides[0]["title"] else slides[0]["title"]
		
		for idx, slide in enumerate(slides):
			# audio - use enhanced content flow
			audio_text = self._compose_slide_tts_text(slide)
			# Remove slide numbering to avoid repetition
			audio_path = self.text_to_speech(audio_text)
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