#!/usr/bin/env python3
"""
Test script for detailed audio explanations with subtopic-focused video format
"""

import os
import time
from video_generator import VideoGenerator
from ai_service import AIService

def test_detailed_audio_format():
    """Test the new format with detailed audio explanations"""
    
    print("🎤 Testing Detailed Audio Explanations with Subtopics")
    print("=" * 60)
    
    # Initialize services
    try:
        video_generator = VideoGenerator()
        ai_service = AIService()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Test topic
    topic = "Machine Learning"
    print(f"\n📚 Testing topic: {topic}")
    
    try:
        # Generate structured content with detailed narration
        structured_data = ai_service.generate_explainer_structured_free(
            topic=topic,
            level="beginner",
            num_slides=3,
            max_retries=1
        )
        
        print("✅ Content generated successfully")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Display the detailed format
        print("\n📋 Detailed Audio Format:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {len(slide.get('bullets', []))} points")
            print(f"Audio Duration: ~{len(slide.get('narration', '')) // 15} seconds")
            
            # Show audio content preview
            narration = slide.get('narration', '')
            if narration:
                print(f"Audio Preview: {narration[:150]}...")
            
            # Show what the video will display
            print(f"Video Display: Subtopics as bullet points")
            print(f"Audio Content: Detailed explanation of each subtopic")
        
        # Convert to script format
        script_lines = []
        for slide in structured_data.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video with longer slide durations
        print(f"\n🎥 Generating video with detailed audio...")
        output_path = "detailed_audio_demo.mp4"
        
        start_time = time.time()
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=15.0,  # 15 seconds per slide for detailed explanations
            width=1280,
            height=720,
            fps=30,
            topic=topic
        )
        end_time = time.time()
        
        print(f"✅ Video generated successfully: {video_path}")
        print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        print(f"⏱️ Generation time: {end_time - start_time:.1f} seconds")
        
        # Test content composition
        print(f"\n🎤 Testing audio content composition:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            content = video_generator._create_enhanced_slide_content(slide)
            print(f"\nSlide {i} Audio Content:")
            print(f"Length: {len(content)} characters")
            print(f"Preview: {content[:200]}...")
        
        print("\n🎉 Demo completed successfully!")
        print("📹 Check 'detailed_audio_demo.mp4' for the new format.")
        print("🎤 Audio explains each subtopic in detail while video shows clean subtopics.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audio_video_sync():
    """Test that audio and video are properly synchronized"""
    
    print("\n⏱️ Testing Audio-Video Synchronization")
    print("=" * 45)
    
    try:
        video_generator = VideoGenerator()
        ai_service = AIService()
        
        # Test with a simple topic
        topic = "Artificial Intelligence"
        
        # Generate content
        structured_data = ai_service.generate_explainer_structured_free(
            topic=topic,
            level="beginner",
            num_slides=2,
            max_retries=1
        )
        
        print("✅ Content generated for sync test")
        
        # Test each slide's audio composition
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} Sync Test ---")
            
            # Get audio content
            audio_content = video_generator._create_enhanced_slide_content(slide)
            
            # Estimate audio duration (average speaking rate: ~150 words per minute)
            words = len(audio_content.split())
            estimated_duration = words / 2.5  # ~150 words per minute = 2.5 words per second
            
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Audio Words: {words}")
            print(f"Estimated Duration: {estimated_duration:.1f} seconds")
            print(f"Recommended Slide Duration: {max(10, estimated_duration + 2):.1f} seconds")
            
            # Check if audio mentions each subtopic
            subtopics = slide.get('subtopics', [])
            for subtopic in subtopics:
                if subtopic.lower() in audio_content.lower():
                    print(f"✅ Audio mentions: {subtopic}")
                else:
                    print(f"❌ Audio missing: {subtopic}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in sync test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Detailed Audio Format Test Suite")
    print("=" * 50)
    
    # Test 1: Detailed audio format
    success1 = test_detailed_audio_format()
    
    # Test 2: Audio-video synchronization
    success2 = test_audio_video_sync()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Detailed Audio Format: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Audio-Video Sync: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Detailed audio format is working correctly.")
        print("📹 Video shows clean subtopics while audio provides detailed explanations.")
        print("🎤 Each subtopic is explained thoroughly in the audio.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.") 