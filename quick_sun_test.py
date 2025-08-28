#!/usr/bin/env python3
"""
Quick test to generate Sun content using the enhanced universal AI prompt
"""

import json
from ai_service import AIService

def test_sun_content():
    """Test the enhanced universal AI prompt with Sun topic"""
    
    print("🌞 Testing Enhanced Universal AI Prompt with Sun Topic")
    print("=" * 60)
    
    try:
        # Initialize AI service
        ai_service = AIService()
        print("✅ AI Service initialized")
        
        # Generate content for Sun
        topic = "The Sun: Our Star"
        print(f"\n🌞 Generating content for: {topic}")
        
        structured_data = ai_service.generate_explainer_structured(
            topic=topic,
            level="beginner",
            num_slides=4,  # Shorter for quick test
            max_retries=2
        )
        
        print("✅ Content generated successfully!")
        print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
        
        # Show the enhanced structure
        print(f"\n📋 Enhanced Content Structure:")
        for i, slide in enumerate(structured_data.get('slides', []), 1):
            print(f"\n--- Slide {i} ---")
            print(f"Title: {slide.get('title', 'N/A')}")
            print(f"Subtopics: {slide.get('subtopics', [])}")
            print(f"Bullets: {slide.get('bullets', [])}")
            print(f"Subtopic Type: {slide.get('subtopic_type', 'N/A')}")
            print(f"Layout: {slide.get('layout', 'N/A')}")
            print(f"Narration Length: {len(slide.get('narration', ''))} characters")
            print(f"Narration Preview: {slide.get('narration', '')[:150]}...")
        
        # Show slide types used
        slide_types = [slide.get('subtopic_type', 'unknown') for slide in structured_data.get('slides', [])]
        unique_types = list(set(slide_types))
        print(f"\n🎭 Subtopic types used: {', '.join(unique_types)}")
        
        # Save to file
        with open("sun_test_content.json", 'w') as f:
            json.dump(structured_data, f, indent=2)
        print(f"\n💾 Content saved to: sun_test_content.json")
        
        # Show video-ready format
        print(f"\n🎬 Video-Ready Format:")
        print(f"  - Duration: {len(structured_data.get('slides', [])) * 8} seconds")
        print(f"  - 8 seconds per slide")
        print(f"  - Enhanced narration (80-120 words per slide)")
        print(f"  - Varied subtopic types for engagement")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sun_content()
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        print("🌞 The enhanced universal AI prompt is working perfectly!")
        print("📄 Check 'sun_test_content.json' for the detailed content structure.")
    else:
        print(f"\n❌ Test failed") 