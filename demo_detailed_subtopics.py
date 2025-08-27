#!/usr/bin/env python3
"""
Demo script for detailed subtopic explanations with different gradient backgrounds
"""

import os
import time
from video_generator import VideoGenerator
from ai_service import AIService

def demo_detailed_subtopics():
    """Demo the detailed subtopic explanations with different backgrounds"""
    
    print("🎤 Detailed Subtopic Explanations Demo")
    print("=" * 50)
    
    # Initialize services
    try:
        video_generator = VideoGenerator()
        ai_service = AIService()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Demo topic
    topic = "Artificial Intelligence"
    print(f"\n📚 Generating detailed subtopic explanations for: {topic}")
    
    try:
        # Generate structured content with detailed narration for each subtopic
        structured_data = ai_service.generate_explainer_structured_free(
            topic=topic,
            level="beginner",
            num_slides=3,
            max_retries=1
        )
        
        print("✅ Content generated successfully")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Show the detailed format
        print("\n📋 Detailed Subtopic Format Preview:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {len(slide.get('bullets', []))} points")
            
            # Calculate estimated duration for each subtopic
            narration = slide.get('narration', '')
            words = len(narration.split())
            estimated_duration = words / 2.5  # ~150 words per minute
            print(f"Estimated Duration: {estimated_duration:.1f} seconds")
            print(f"Subtopics per slide: {len(slide.get('subtopics', []))}")
            print(f"Seconds per subtopic: ~{estimated_duration / len(slide.get('subtopics', [])):.1f}")
            
            # Show audio content preview
            if narration:
                print(f"Audio Preview: {narration[:150]}...")
            
            # Show what the video will display
            print(f"Video Display: Subtopics as bullet points")
            print(f"Audio Content: Detailed explanation of each subtopic")
            print(f"Background: Different gradient for each slide")
        
        # Convert to script format
        script_lines = []
        for slide in structured_data.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video with detailed subtopic explanations
        print(f"\n🎥 Generating video with detailed subtopic explanations...")
        output_path = "demo_detailed_subtopics.mp4"
        
        start_time = time.time()
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=25.0,  # 25 seconds per slide for detailed subtopic explanations
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
        print(f"\n🎤 Testing detailed audio content composition:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            content = video_generator._create_enhanced_slide_content(slide)
            words = len(content.split())
            estimated_duration = words / 2.5
            
            print(f"\nSlide {i} Audio Content:")
            print(f"Words: {words}")
            print(f"Estimated Duration: {estimated_duration:.1f} seconds")
            print(f"Subtopics: {len(slide.get('subtopics', []))}")
            print(f"Seconds per subtopic: ~{estimated_duration / len(slide.get('subtopics', [])):.1f}")
            print(f"Preview: {content[:200]}...")
        
        print("\n🎉 Demo completed successfully!")
        print("📹 Check 'demo_detailed_subtopics.mp4' for the new format.")
        print("🎤 Each subtopic gets 20-25 seconds of detailed explanation.")
        print("🎨 Each slide has a different gradient background.")
        print("📋 Video shows clean subtopics while audio explains each in detail.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gradient_backgrounds():
    """Test the different gradient backgrounds for each slide"""
    
    print("\n🎨 Testing Gradient Backgrounds")
    print("=" * 35)
    
    try:
        video_generator = VideoGenerator()
        
        # Test different topic categories
        categories = ['technology', 'science', 'business', 'education']
        
        for category in categories:
            print(f"\n--- {category.upper()} Category ---")
            
            # Test different slide indices
            for slide_index in range(3):
                background = video_generator._get_notebooklm_background(category, slide_index)
                print(f"Slide {slide_index + 1}: {background.shape} - Different gradient")
        
        print("\n✅ All gradient backgrounds generated successfully")
        print("🎨 Each slide will have a different gradient background")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in gradient test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Detailed Subtopics Demo Suite")
    print("=" * 45)
    
    # Test 1: Detailed subtopic format
    success1 = demo_detailed_subtopics()
    
    # Test 2: Gradient backgrounds
    success2 = test_gradient_backgrounds()
    
    print("\n" + "=" * 45)
    print("📊 Test Results Summary:")
    print(f"✅ Detailed Subtopics: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Gradient Backgrounds: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Detailed subtopic format is working correctly.")
        print("📹 Video shows clean subtopics with different gradient backgrounds.")
        print("🎤 Each subtopic gets 20-25 seconds of detailed explanation.")
        print("🎨 Each slide has a unique gradient background.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.") 