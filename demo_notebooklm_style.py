#!/usr/bin/env python3
"""
Demo script for NotebookLM-style video generation
"""

import os
from ai_service import AIService
from video_generator import VideoGenerator

def demo_notebooklm_style():
    """Demo the NotebookLM-style video generation"""
    
    print("🎬 NotebookLM-Style Video Generation Demo")
    print("=" * 50)
    
    # Initialize services
    try:
        ai_service = AIService()
        video_generator = VideoGenerator()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # Demo topic
    topic = "Artificial Intelligence Basics"
    print(f"\n📚 Generating NotebookLM-style presentation for: {topic}")
    
    try:
        # Generate structured content
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
        
        # Display the structure
        print("\n📋 Presentation Structure:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {len(slide.get('bullets', []))} points")
            print(f"Narration: {len(slide.get('narration', ''))} characters")
        
        # Convert to script format
        script_lines = []
        for slide in structured_data.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video
        print(f"\n🎥 Generating NotebookLM-style video...")
        output_path = "notebooklm_style_demo.mp4"
        
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=8.0,
            width=1280,
            height=720,
            fps=30,
            topic=topic
        )
        
        print(f"✅ Video generated successfully: {video_path}")
        print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        
        print("\n🎉 Demo completed successfully!")
        print("📹 Check 'notebooklm_style_demo.mp4' for the new NotebookLM-style video.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    demo_notebooklm_style() 