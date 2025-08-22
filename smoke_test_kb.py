#!/usr/bin/env python3
from video_generator import VideoGenerator
from config import Config


def main():
	cfg = Config()
	gen = VideoGenerator()
	if gen.default_background is None:
		print("Default background not loaded; cannot run cover test.")
		return
	w, h = cfg.DEFAULT_VIDEO_WIDTH, cfg.DEFAULT_VIDEO_HEIGHT
	frame = gen._ken_burns_frame(gen.default_background, w, h, t=0.5, total=5.0)
	print("Frame shape:", frame.shape)
	assert frame.shape[0] == h and frame.shape[1] == w, "Frame does not match target dimensions"
	print("OK: Background covers the full frame.")


if __name__ == "__main__":
	main()
