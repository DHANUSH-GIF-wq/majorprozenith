#!/usr/bin/env python3
"""
Demo script for Sun video generation using the enhanced universal AI prompt
"""

import os
import json
from ai_service import AIService
from video_generator import VideoGenerator

def demo_sun_video():
    """Demo the enhanced video generation system with Sun topic"""
    
    print("🌞 Sun Video Generation Demo")
    print("=" * 50)
    
    # Initialize services
    try:
        ai_service = AIService()
        video_generator = VideoGenerator()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Demo topic: The Sun
    topic = "The Sun: Our Star"
    print(f"\n🌞 Generating enhanced video presentation for: {topic}")
    
    try:
        # Generate structured content using the enhanced universal prompt
        print("🔄 Generating content with universal AI prompt...")
        structured_data = ai_service.generate_explainer_structured(
            topic=topic,
            level="beginner",
            num_slides=6,
            max_retries=2
        )
        
        print("✅ Content generated successfully")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Show topic categorization
        topic_category = ai_service._categorize_topic(topic)
        print(f"🏷️ Topic category: {topic_category}")
        
        # Display the enhanced structure
        print("\n📋 Enhanced Presentation Structure:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {len(slide.get('bullets', []))} points")
            print(f"Narration: {len(slide.get('narration', ''))} characters")
            print(f"Subtopic Type: {slide.get('subtopic_type', 'N/A')}")
            print(f"Layout: {slide.get('layout', 'N/A')}")
        
        # Show slide types used
        slide_types = [slide.get('subtopic_type', 'unknown') for slide in structured_data.get('slides', [])]
        unique_types = list(set(slide_types))
        print(f"\n🎭 Subtopic types used: {', '.join(unique_types)}")
        
        # Save structured data to file
        output_file = "sun_video_content.json"
        with open(output_file, 'w') as f:
            json.dump(structured_data, f, indent=2)
        print(f"💾 Structured data saved to: {output_file}")
        
        # Convert to script format for video generation
        script_lines = []
        for slide in structured_data.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video
        print(f"\n🎥 Generating enhanced Sun video...")
        output_path = "sun_demo_video.mp4"
        
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=8.0,  # 8 seconds per slide as per universal prompt
            width=1280,
            height=720,
            fps=30,
            topic=topic
        )
        
        print(f"✅ Video generated successfully: {video_path}")
        print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        
        # Show video details
        print(f"\n🎬 Video Details:")
        print(f"  - Duration: {len(structured_data.get('slides', [])) * 8} seconds")
        print(f"  - Resolution: 1280x720")
        print(f"  - FPS: 30")
        print(f"  - Topic: {topic}")
        print(f"  - Category: {topic_category}")
        
        print("\n🎉 Sun video demo completed successfully!")
        print("📹 Check 'sun_demo_video.mp4' for the enhanced video presentation.")
        print("📄 Check 'sun_video_content.json' for the detailed content structure.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_content_preview():
    """Show a preview of the generated content"""
    
    print("\n📋 Content Preview:")
    print("=" * 30)
    
    try:
        with open("sun_video_content.json", 'r') as f:
            data = json.load(f)
        
        print(f"Topic: {data.get('topic', 'N/A')}")
        print(f"Level: {data.get('level', 'N/A')}")
        print(f"Slides: {len(data.get('slides', []))}")
        
        print(f"\nSample Slide Content:")
        if data.get('slides'):
            slide = data['slides'][0]
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {slide.get('bullets', [])}")
            print(f"Narration Preview: {slide.get('narration', '')[:100]}...")
            print(f"Subtopic Type: {slide.get('subtopic_type', 'N/A')}")
            print(f"Layout: {slide.get('layout', 'N/A')}")
        
    except FileNotFoundError:
        print("No content file found. Run the demo first.")
    except Exception as e:
        print(f"Error reading content: {e}")

if __name__ == "__main__":
    print("🌞 Starting Sun Video Demo with Enhanced Universal AI Prompt")
    
    # Run the demo
    success = demo_sun_video()
    
    if success:
        # Show content preview
        show_content_preview()
        print("\n🎉 Demo completed successfully!")
        print("🌞 The enhanced universal AI prompt system is working perfectly!")
    else:
        print("\n❌ Demo failed")
    
    print("\n📖 The system now uses the enhanced universal AI prompt with:")
    print("  - 8 different subtopic types for variety")
    print("  - Video-optimized content (8 seconds per slide)")
    print("  - Enhanced narration (80-120 words per slide)")
    print("  - Animation suggestions for each slide type")
    print("  - Professional video flow between slides") 