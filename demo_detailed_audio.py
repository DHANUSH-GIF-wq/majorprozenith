#!/usr/bin/env python3
"""
Demo script for detailed audio format with subtopics
"""

import os
from video_generator import VideoGenerator
from ai_service import AIService

def demo_detailed_audio():
    """Demo the detailed audio format with subtopics"""
    
    print("🎤 Detailed Audio Format Demo")
    print("=" * 40)
    
    # Initialize services
    try:
        video_generator = VideoGenerator()
        ai_service = AIService()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Demo topic
    topic = "Quantum Physics"
    print(f"\n📚 Generating detailed audio format for: {topic}")
    
    try:
        # Generate structured content with detailed narration
        structured_data = ai_service.generate_explainer_structured_free(
            topic=topic,
            level="beginner",
            num_slides=2,
            max_retries=1
        )
        
        print("✅ Content generated successfully")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Show the new format
        print("\n📋 New Format Preview:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Video Shows: {slide.get('subtopics', [])}")
            print(f"Audio Explains: {len(slide.get('narration', ''))} characters")
            
            # Show audio preview
            narration = slide.get('narration', '')
            if narration:
                print(f"Audio Preview: {narration[:100]}...")
        
        # Convert to script format
        script_lines = []
        for slide in structured_data.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video with detailed audio format
        print(f"\n🎥 Generating video with detailed audio...")
        output_path = "demo_detailed_audio.mp4"
        
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=15.0,  # 15 seconds per slide for detailed explanations
            width=1280,
            height=720,
            fps=30,
            topic=topic
        )
        
        print(f"✅ Video generated successfully: {video_path}")
        print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        
        print("\n🎉 Demo completed successfully!")
        print("📹 Check 'demo_detailed_audio.mp4' for the new format.")
        print("🎤 Video shows subtopics while audio explains each in detail.")
        print("⏱️ Extended duration for comprehensive coverage.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    demo_detailed_audio() 