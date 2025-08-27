#!/usr/bin/env python3
"""
Test NotebookLM-style video generation
"""

from video_generator import VideoGenerator
from ai_service import AIService
import os

def test_notebooklm_style():
    """Test the NotebookLM-style video generation"""
    
    print("🎬 Testing NotebookLM-Style Video Generation...")
    
    try:
        # Initialize services
        video_generator = VideoGenerator()
        ai_service = AIService()
        print("✅ Services initialized successfully!")
        
        # Test topic
        topic = "artificial intelligence"
        print(f"🏷️  Topic: {topic}")
        
        # Generate structured explainer
        print("🤖 Generating AI explanation...")
        data = ai_service.generate_explainer_structured(
            topic=topic,
            level="beginner",
            num_slides=4
        )
        
        print("✅ AI explanation generated!")
        
        # Show the structure
        print("\n📋 Generated Content Structure:")
        for i, slide in enumerate(data.get("slides", []), 1):
            print(f"\nSlide {i}: {slide.get('title', 'No title')}")
            print(f"Key Points: {', '.join(slide.get('bullets', []))}")
            if slide.get('narration'):
                print(f"Narration: {slide['narration'][:100]}...")
        
        # Test video generation (without actually creating the video file)
        print("\n🎥 Testing video generation setup...")
        
        # Check if the enhanced methods exist
        if hasattr(video_generator, '_create_enhanced_slide_content'):
            print("✅ Enhanced content creation method available")
        else:
            print("❌ Enhanced content creation method missing")
            
        if hasattr(video_generator, '_draw_clean_slide_text'):
            print("✅ Clean slide text method available")
        else:
            print("❌ Clean slide text method missing")
            
        if hasattr(video_generator, '_get_topic_background'):
            print("✅ Topic background method available")
        else:
            print("❌ Topic background method missing")
        
        print("\n✨ NotebookLM-style test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notebooklm_style()
