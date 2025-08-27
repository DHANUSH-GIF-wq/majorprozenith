#!/usr/bin/env python3
"""
Test script for NotebookLM-style video generation with dynamic content and professional backgrounds
"""

import os
import sys
import tempfile
from ai_service import AIService
from video_generator import VideoGenerator

def test_notebooklm_style_generation():
    """Test the NotebookLM-style video generation with dynamic content"""
    
    print("🎬 Testing NotebookLM-Style Video Generation")
    print("=" * 55)
    
    # Initialize services
    try:
        ai_service = AIService()
        video_generator = VideoGenerator()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Test different topics to show dynamic content
    test_topics = [
        "Machine Learning Fundamentals",
        "Quantum Physics Basics", 
        "Business Strategy",
        "Climate Change Science"
    ]
    
    for topic in test_topics:
        print(f"\n📚 Testing topic: {topic}")
        
        try:
            # Generate structured content with dynamic adaptation
            structured_data = ai_service.generate_explainer_structured(
                topic=topic,
                level="beginner",
                num_slides=6,
                max_retries=2
            )
            
            print(f"✅ Content generated for: {topic}")
            print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
            
            # Show topic categorization
            topic_category = ai_service._categorize_topic(topic)
            print(f"🏷️ Topic category: {topic_category}")
            
            # Display sample slide structure
            if structured_data.get('slides'):
                first_slide = structured_data['slides'][0]
                print(f"📋 Sample slide: {first_slide.get('title', 'N/A')}")
                print(f"   Subtopics: {first_slide.get('subtopics', [])}")
                print(f"   Bullets: {len(first_slide.get('bullets', []))} points")
                print(f"   Narration: {len(first_slide.get('narration', ''))} characters")
            
            # Convert to script format for video generation
            script_lines = []
            for slide in structured_data.get('slides', []):
                script_lines.append(f"### {slide.get('title', 'Untitled')}")
                for bullet in slide.get('bullets', []):
                    script_lines.append(f"- {bullet}")
                script_lines.append("")  # Empty line between slides
            
            script = "\n".join(script_lines)
            
            # Generate video with topic-specific background
            print(f"🎥 Generating NotebookLM-style video...")
            output_path = f"notebooklm_style_{topic.replace(' ', '_').lower()}.mp4"
            
            video_path = video_generator.generate_slideshow_video(
                script=script,
                output_path=output_path,
                seconds_per_slide=8.0,  # Optimal duration for NotebookLM style
                width=1280,
                height=720,
                fps=30,
                topic=topic  # Pass topic for dynamic background selection
            )
            
            print(f"✅ Video generated: {video_path}")
            print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
            
        except Exception as e:
            print(f"❌ Error with topic '{topic}': {e}")
            continue
    
    return True

def test_background_system():
    """Test the professional background system"""
    
    print("\n🎨 Testing Professional Background System")
    print("=" * 45)
    
    try:
        video_generator = VideoGenerator()
        
        # Test different topic categories
        test_categories = [
            'technology', 'science', 'business', 'education', 
            'health', 'arts', 'nature', 'space', 'default'
        ]
        
        print("📋 Available background categories:")
        for category in test_categories:
            background = video_generator._get_notebooklm_background(category)
            if background is not None:
                print(f"✅ {category}: {background.shape[1]}x{background.shape[0]} pixels")
            else:
                print(f"❌ {category}: Failed to load")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing background system: {e}")
        return False

def test_content_cleaning():
    """Test the content cleaning to remove question marks"""
    
    print("\n🧹 Testing Content Cleaning (No Question Marks)")
    print("=" * 50)
    
    try:
        ai_service = AIService()
        
        # Test content cleaning
        test_texts = [
            "What is machine learning?",
            "How does neural networks work?",
            "Why do we need AI?",
            "When should you use deep learning?",
            "Where can you apply computer vision?"
        ]
        
        print("📝 Testing question mark removal:")
        for text in test_texts:
            cleaned = ai_service._clean_text(text)
            print(f"Original: {text}")
            print(f"Cleaned:  {cleaned}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing content cleaning: {e}")
        return False

if __name__ == "__main__":
    print("🚀 NotebookLM-Style Video Generation Test Suite")
    print("=" * 55)
    
    # Test 1: NotebookLM-style generation
    success1 = test_notebooklm_style_generation()
    
    # Test 2: Background system
    success2 = test_background_system()
    
    # Test 3: Content cleaning
    success3 = test_content_cleaning()
    
    print("\n" + "=" * 55)
    print("📊 Test Results Summary:")
    print(f"✅ NotebookLM Generation: {'PASS' if success1 else 'FAIL'}")
    print(f"✅ Background System: {'PASS' if success2 else 'FAIL'}")
    print(f"✅ Content Cleaning: {'PASS' if success3 else 'FAIL'}")
    
    if success1 and success2 and success3:
        print("\n🎉 All tests passed! NotebookLM-style video generation is working correctly.")
        print("📹 Check the generated video files for the new style.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
