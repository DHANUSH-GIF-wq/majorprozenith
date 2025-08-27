#!/usr/bin/env python3
"""
Test improved content generation without question marks
"""

from ai_service import AIService
import json

def test_improved_content():
    """Test the improved content generation"""
    
    print("🧪 Testing Improved Content Generation...")
    
    try:
        # Initialize AI service
        ai_service = AIService()
        print("✅ AI service initialized successfully!")
        
        # Test topics of different complexity
        test_topics = [
            "AI",  # Simple topic
            "Machine Learning Basics",  # Medium topic
            "Quantum Computing and its Applications in Cryptography"  # Complex topic
        ]
        
        for topic in test_topics:
            print(f"\n🎯 Testing topic: '{topic}'")
            print("-" * 50)
            
            try:
                # Generate structured explainer
                data = ai_service.generate_explainer_structured(
                    topic=topic,
                    level="beginner",
                    num_slides=4
                )
                
                print(f"✅ Generated {len(data.get('slides', []))} slides")
                
                # Check for question marks
                question_marks_found = False
                for i, slide in enumerate(data.get("slides", []), 1):
                    print(f"\n📝 Slide {i}: {slide.get('title', 'No title')}")
                    
                    # Check title
                    if "?" in slide.get("title", ""):
                        print(f"   ❌ Question mark in title: {slide['title']}")
                        question_marks_found = True
                    
                    # Check bullets
                    for j, bullet in enumerate(slide.get("bullets", [])):
                        if "?" in bullet:
                            print(f"   ❌ Question mark in bullet {j+1}: {bullet}")
                            question_marks_found = True
                        else:
                            print(f"   ✅ Bullet {j+1}: {bullet}")
                    
                    # Check narration
                    narration = slide.get("narration", "")
                    if "?" in narration:
                        print(f"   ❌ Question mark in narration: {narration[:100]}...")
                        question_marks_found = True
                    else:
                        print(f"   ✅ Narration: {narration[:100]}...")
                
                if not question_marks_found:
                    print(f"\n✨ Topic '{topic}' - No question marks found!")
                else:
                    print(f"\n⚠️  Topic '{topic}' - Some question marks found")
                
            except Exception as e:
                print(f"❌ Failed to generate content for '{topic}': {e}")
        
        print("\n🎉 Content generation test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_content()
