#!/usr/bin/env python3
"""
Example script demonstrating the new background image functionality
"""

from video_generator import VideoGenerator

def main():
    """Demonstrate background image usage"""
    print("Background Image Video Generation Example")
    print("=" * 50)
    
    # Create video generator (automatically loads testbg.jpeg as background)
    generator = VideoGenerator()
    
    print(f"✅ Video generator created with background image")
    if generator.default_background is not None:
        print(f"   Background dimensions: {generator.default_background.shape}")
    
    # Example 1: Generate a simple typewriter video with background
    print("\n📹 Example 1: Typewriter video with background")
    try:
        text = "This is a sample video with the testbg.jpeg image as background. The text will appear on top of this background image with a nice overlay effect."
        
        output_path = "example_typewriter_video.mp4"
        result = generator.generate_video(
            text=text,
            duration=10,
            output_path=output_path
        )
        print(f"   ✅ Video generated: {result}")
    except Exception as e:
        print(f"   ❌ Error generating video: {e}")
    
    # Example 2: Generate a slideshow with background
    print("\n📹 Example 2: Slideshow video with background")
    try:
        script = """### Introduction
- Welcome to our presentation
- This slide uses the background image

### Main Points
- Point one with background
- Point two with background
- Point three with background

### Conclusion
- Thank you for watching
- Background image makes it look professional"""
        
        output_path = "example_slideshow_video.mp4"
        result = generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=3
        )
        print(f"   ✅ Slideshow generated: {result}")
    except Exception as e:
        print(f"   ❌ Error generating slideshow: {e}")
    
    # Example 3: Change background image (if you have another image)
    print("\n🔄 Example 3: Changing background image")
    print("   You can use generator.set_default_background('path/to/image.jpg')")
    print("   to change the background for future videos")
    
    print("\n🎉 Background image integration complete!")
    print("   All videos will now use testbg.jpeg as the background")
    print("   Text overlays are automatically adjusted for readability")

if __name__ == "__main__":
    main()
