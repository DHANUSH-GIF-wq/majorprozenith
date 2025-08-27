#!/usr/bin/env python3
"""
Test script for enhanced video generation with professional presentation format
"""

import os
import sys
import tempfile
from ai_service import AIService
from video_generator import VideoGenerator

def test_enhanced_presentation():
    """Test the enhanced presentation generation with subtopics and detailed content"""
    
    print("🎬 Testing Enhanced Professional Presentation Generation")
    print("=" * 60)
    
    # Initialize services
    try:
        ai_service = AIService()
        video_generator = VideoGenerator()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Test topic
    topic = "Machine Learning Fundamentals"
    print(f"\n📚 Generating professional presentation for: {topic}")
    
    try:
        # Generate structured content with subtopics
        structured_data = ai_service.generate_explainer_structured(
            topic=topic,
            level="beginner",
            num_slides=8,
            max_retries=2
        )
        
        print("✅ Structured content generated successfully")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Display the structure
        print("\n📋 Presentation Structure:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {len(slide.get('bullets', []))} points")
            print(f"Narration: {len(slide.get('narration', ''))} characters")
            print(f"Examples: {len(slide.get('examples', []))} examples")
        
        # Convert to script format for video generation
        script_lines = []
        for slide in structured_data.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")  # Empty line between slides
        
        script = "\n".join(script_lines)
        
        # Generate video
        print(f"\n🎥 Generating professional presentation video...")
        output_path = "enhanced_presentation_demo.mp4"
        
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=10.0,  # Longer duration for detailed content
            width=1280,
            height=720,
            fps=30
        )
        
        print(f"✅ Video generated successfully: {video_path}")
        print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detailed_content_flow():
    """Test the detailed content flow and narration"""
    
    print("\n🎯 Testing Detailed Content Flow")
    print("=" * 40)
    
    # Sample slide with subtopics and detailed content
    sample_slide = {
        "title": "Introduction to Neural Networks",
        "subtopics": ["Basic Structure", "Learning Process", "Applications"],
        "bullets": [
            "Neural networks mimic human brain connections",
            "They learn patterns from training data",
            "Used in image recognition and language processing",
            "Can solve complex problems automatically"
        ],
        "narration": "Neural networks are powerful computational models inspired by the human brain. They consist of interconnected nodes that process information in layers. The basic structure includes input layers that receive data, hidden layers that perform computations, and output layers that provide results. The learning process involves adjusting connection weights based on training examples, allowing the network to recognize patterns and make predictions. These systems are widely used in modern applications like facial recognition, voice assistants, and autonomous vehicles, demonstrating their versatility in solving complex real-world problems.",
        "examples": [
            "Google's image search uses neural networks",
            "Siri and Alexa rely on neural networks for speech recognition"
        ]
    }
    
    try:
        video_generator = VideoGenerator()
        
        # Test content composition
        content = video_generator._create_enhanced_slide_content(sample_slide)
        print("✅ Content composition successful")
        print(f"📝 Generated content length: {len(content)} characters")
        print(f"📝 Content preview: {content[:200]}...")
        
        # Test TTS generation
        audio_path = video_generator.text_to_speech(content)
        print(f"✅ TTS generation successful: {audio_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in content flow test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Video Generation Test Suite")
    print("=" * 50)
    
    # Test 1: Enhanced presentation generation
    success1 = test_enhanced_presentation()
    
    # Test 2: Detailed content flow
    success2 = test_detailed_content_flow()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Enhanced Presentation: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Content Flow: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Enhanced video generation is working correctly.")
        print("📹 Check 'enhanced_presentation_demo.mp4' for the generated video.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
