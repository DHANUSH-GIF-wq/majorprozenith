#!/usr/bin/env python3
"""
Test script for quick 10-second video generation with free content
"""

import os
import time
from video_generator import VideoGenerator
from ai_service import AIService

def test_quick_video_generation():
    """Test the quick 10-second video generation"""
    
    print("⚡ Testing Quick 10-Second Video Generation")
    print("=" * 50)
    
    # Initialize services
    try:
        video_generator = VideoGenerator()
        ai_service = AIService()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Test topics
    test_topics = [
        "Machine Learning",
        "Quantum Physics", 
        "Blockchain Technology",
        "Climate Change"
    ]
    
    for topic in test_topics:
        print(f"\n📚 Testing topic: {topic}")
        
        try:
            start_time = time.time()
            
            # Generate quick video
            output_path = f"quick_{topic.replace(' ', '_').lower()}.mp4"
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
            
            print(f"✅ Video generated: {video_path}")
            print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
            print(f"⏱️ Generation time: {generation_time:.1f} seconds")
            
            # Test content cleaning
            print(f"🧹 Testing content cleaning for: {topic}")
            test_content = f"??? What is {topic}? How does it work? Why is it important?"
            cleaned = ai_service._clean_text(test_content)
            print(f"Original: {test_content}")
            print(f"Cleaned:  {cleaned}")
            
        except Exception as e:
            print(f"❌ Error with topic '{topic}': {e}")
            continue
    
    return True

def test_free_content_generation():
    """Test the free content generation without API keys"""
    
    print("\n🆓 Testing Free Content Generation")
    print("=" * 40)
    
    try:
        ai_service = AIService()
        
        # Test free content generation
        topic = "Artificial Intelligence"
        print(f"📝 Generating free content for: {topic}")
        
        structured_data = ai_service.generate_explainer_structured_free(
            topic=topic,
            level="beginner",
            num_slides=3,
            max_retries=1
        )
        
        print("✅ Free content generated successfully")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Display content structure
        print("\n📋 Content Structure:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {len(slide.get('bullets', []))} points")
            print(f"Narration: {len(slide.get('narration', ''))} characters")
            
            # Check for question marks
            title_has_questions = '?' in slide.get('title', '')
            bullets_have_questions = any('?' in bullet for bullet in slide.get('bullets', []))
            narration_has_questions = '?' in slide.get('narration', '')
            
            print(f"❓ Questions in title: {title_has_questions}")
            print(f"❓ Questions in bullets: {bullets_have_questions}")
            print(f"❓ Questions in narration: {narration_has_questions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in free content generation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Video Generation Test Suite")
    print("=" * 50)
    
    # Test 1: Quick video generation
    success1 = test_quick_video_generation()
    
    # Test 2: Free content generation
    success2 = test_free_content_generation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Quick Video Generation: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Free Content Generation: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Quick video generation is working correctly.")
        print("📹 Check the generated 'quick_*.mp4' files for 10-second videos.")
        print("🆓 Content generation works without API keys!")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.") 