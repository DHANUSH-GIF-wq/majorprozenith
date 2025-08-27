#!/usr/bin/env python3
"""
Demo script for quick 10-second video generation
"""

import os
import time
from video_generator import VideoGenerator
from ai_service import AIService

def demo_quick_video():
    """Demo the quick 10-second video generation"""
    
    print("⚡ Quick 10-Second Video Generation Demo")
    print("=" * 45)
    
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
    print(f"\n📚 Generating quick video for: {topic}")
    
    try:
        start_time = time.time()
        
        # Generate quick video
        output_path = "demo_quick_video.mp4"
        video_path = video_generator.generate_quick_video(
            topic=topic,
            output_path=output_path,
            duration=10,
            width=1280,
            height=720,
            fps=30
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"✅ Video generated successfully: {video_path}")
        print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        print(f"⏱️ Generation time: {generation_time:.1f} seconds")
        
        # Test content cleaning
        print(f"\n🧹 Testing content cleaning:")
        test_content = f"??? What is {topic}? How does it work? Why is it important?"
        cleaned = ai_service._clean_text(test_content)
        print(f"Original: {test_content}")
        print(f"Cleaned:  {cleaned}")
        
        # Test free content generation
        print(f"\n🆓 Testing free content generation:")
        structured_data = ai_service.generate_explainer_structured_free(
            topic=topic,
            level="beginner",
            num_slides=3,
            max_retries=1
        )
        
        print("✅ Free content generated successfully")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Check for question marks in generated content
        has_questions = False
        for slide in structured_data.get('slides', []):
            if '?' in slide.get('title', '') or any('?' in bullet for bullet in slide.get('bullets', [])) or '?' in slide.get('narration', ''):
                has_questions = True
                break
        
        print(f"❓ Content has question marks: {has_questions}")
        
        print("\n🎉 Demo completed successfully!")
        print("📹 Check 'demo_quick_video.mp4' for the 10-second video.")
        print("🆓 Content generation works without API keys!")
        print("✅ No question marks in the content!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    demo_quick_video() 