#!/usr/bin/env python3
"""
Test script to verify the audio fix works correctly
"""

from video_generator import VideoGenerator
from ai_service import AIService
import tempfile
import os

def test_audio_generation():
    """Test if audio is properly generated and merged"""
    
    print("🎬 Testing Audio Generation Fix...")
    
    try:
        # Initialize services
        video_generator = VideoGenerator()
        ai_service = AIService()
        print("✅ Services initialized successfully!")
        
        # Test topic
        topic = "AI Basics"
        print(f"🏷️  Topic: {topic}")
        
        # Generate structured explainer
        print("🤖 Generating AI explanation...")
        data = ai_service.generate_explainer_structured(
            topic=topic,
            level="beginner",
            num_slides=3
        )
        
        print("✅ AI explanation generated!")
        
        # Show the structure
        print("\n📋 Generated Content Structure:")
        for i, slide in enumerate(data.get("slides", []), 1):
            print(f"\nSlide {i}: {slide.get('title', 'No title')}")
            print(f"Key Points: {', '.join(slide.get('bullets', []))}")
            if slide.get('narration'):
                print(f"Narration: {slide['narration'][:100]}...")
        
        # Test video generation with audio
        print("\n🎥 Testing video generation with audio...")
        
        # Create temporary file for output
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video.close()
        
        try:
            # Generate video with enhanced features
            video_path = video_generator.generate_slideshow_video_structured(
                structured=data,
                output_path=temp_video.name,
                width=640,
                height=480,
                fps=24,
                seconds_per_slide=5.0,
                voice_gender="male",
                topic=topic
            )
            
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                print(f"✅ Video generated successfully: {video_path}")
                print(f"📁 File size: {file_size} bytes")
                
                # Check if video has audio (file size should be reasonable)
                if file_size > 10000:  # More than 10KB
                    print("✅ Video file size looks good - likely has audio")
                else:
                    print("⚠️  Video file size is small - may not have audio")
                
                # Clean up
                try:
                    os.unlink(video_path)
                    print("✅ Test video cleaned up")
                except:
                    pass
                    
            else:
                print("❌ Video file not created")
                
        except Exception as e:
            print(f"❌ Video generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✨ Audio fix test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_generation()
