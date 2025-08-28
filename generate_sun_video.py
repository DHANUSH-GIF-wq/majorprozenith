#!/usr/bin/env python3
"""
Generate Sun video using the enhanced universal AI prompt system
"""

import json
import os
from video_generator import VideoGenerator

def generate_sun_video():
    """Generate the Sun video using the enhanced system"""
    
    print("🌞 Generating Sun Video")
    print("=" * 40)
    
    try:
        # Initialize video generator
        video_generator = VideoGenerator()
        print("✅ Video generator initialized")
        
        # Load the generated content
        with open("sun_video_content.json", 'r') as f:
            structured_data = json.load(f)
        
        print(f"📄 Loaded content for: {structured_data.get('topic', 'Unknown')}")
        print(f"📊 Found {len(structured_data.get('slides', []))} slides")
        
        # Convert to script format
        script_lines = []
        for slide in structured_data.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video
        print("🎥 Generating video...")
        output_path = "sun_video.mp4"
        
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=8.0,
            width=1280,
            height=720,
            fps=30,
            topic="The Sun: Our Star"
        )
        
        print(f"✅ Video generated successfully!")
        print(f"📁 File: {video_path}")
        print(f"📏 Size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_sun_video()
    
    if success:
        print("\n🎉 Sun video generated successfully!")
        print("📹 Check 'sun_video.mp4' for your video!")
    else:
        print("\n❌ Failed to generate video") 