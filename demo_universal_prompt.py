#!/usr/bin/env python3
"""
Demo script for Universal AI Prompt System
Tests the system with different topics and shows its capabilities
"""

import os
import json
from universal_ai_prompt import UniversalAIPrompt

def demo_universal_prompt():
    """Demo the Universal AI Prompt system with multiple topics"""
    
    print("🎬 Universal AI Prompt System Demo")
    print("=" * 60)
    
    # Initialize the system
    try:
        universal_prompt = UniversalAIPrompt()
        print("✅ Universal AI Prompt system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return False
    
    # Demo topics with different categories
    demo_topics = [
        {
            "topic": "Machine Learning Fundamentals",
            "level": "beginner",
            "slides": 6,
            "description": "Technology topic with definition, process, and case study types"
        },
        {
            "topic": "Climate Change Science",
            "level": "intermediate", 
            "slides": 7,
            "description": "Science topic with timeline, classification, and advantages/disadvantages"
        },
        {
            "topic": "Digital Marketing Strategies",
            "level": "intermediate",
            "slides": 6,
            "description": "Business topic with process, advantages/disadvantages, and case study"
        }
    ]
    
    results = []
    
    for i, demo in enumerate(demo_topics, 1):
        print(f"\n{'='*20} Demo {i}: {demo['topic']} {'='*20}")
        print(f"📚 Topic: {demo['topic']}")
        print(f"📊 Level: {demo['level']}")
        print(f"📋 Slides: {demo['slides']}")
        print(f"📝 Description: {demo['description']}")
        
        try:
            # Generate structured content
            print(f"\n🔄 Generating content...")
            structured_data = universal_prompt.generate_structured_content(
                topic=demo['topic'],
                level=demo['level'],
                num_slides=demo['slides'],
                max_retries=2
            )
            
            print(f"✅ Content generated successfully")
            print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
            print(f"🏷️ Topic category: {structured_data.get('category', 'N/A')}")
            print(f"📈 Complexity: {structured_data.get('complexity', 'N/A')}")
            
            # Show slide types used
            slide_types = [slide.get('subtopic_type', 'unknown') for slide in structured_data.get('slides', [])]
            unique_types = list(set(slide_types))
            print(f"🎭 Slide types used: {', '.join(unique_types)}")
            
            # Show slide titles
            print(f"\n📋 Slide Titles:")
            for j, slide in enumerate(structured_data.get('slides', []), 1):
                title = slide.get('title', 'Untitled')
                subtopic_type = slide.get('subtopic_type', 'unknown')
                print(f"  {j}. {title} ({subtopic_type})")
            
            # Save structured data to file
            output_file = f"universal_demo_{i}_{demo['topic'].lower().replace(' ', '_')}.json"
            with open(output_file, 'w') as f:
                json.dump(structured_data, f, indent=2)
            print(f"💾 Structured data saved to: {output_file}")
            
            # Generate video (optional - can be slow)
            generate_video = input(f"\n🎥 Generate video for '{demo['topic']}'? (y/n): ").lower().strip()
            if generate_video == 'y':
                print(f"🎬 Generating video...")
                video_path = universal_prompt.generate_video_from_content(structured_data)
                print(f"✅ Video generated: {video_path}")
                print(f"📁 File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
            else:
                print("⏭️ Skipping video generation")
            
            # Store results
            results.append({
                "topic": demo['topic'],
                "success": True,
                "slides": len(structured_data.get('slides', [])),
                "category": structured_data.get('category', 'N/A'),
                "complexity": structured_data.get('complexity', 'N/A'),
                "slide_types": unique_types,
                "output_file": output_file
            })
            
        except Exception as e:
            print(f"❌ Error processing {demo['topic']}: {e}")
            import traceback
            traceback.print_exc()
            
            results.append({
                "topic": demo['topic'],
                "success": False,
                "error": str(e)
            })
            continue
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 DEMO SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n📋 Successful Topics:")
        for result in successful:
            print(f"  • {result['topic']}")
            print(f"    - Slides: {result['slides']}")
            print(f"    - Category: {result['category']}")
            print(f"    - Types: {', '.join(result['slide_types'])}")
            print(f"    - Output: {result['output_file']}")
    
    if failed:
        print(f"\n❌ Failed Topics:")
        for result in failed:
            print(f"  • {result['topic']}: {result['error']}")
    
    print(f"\n🎉 Universal AI Prompt demo completed!")
    print(f"📁 Check the generated JSON files for detailed content structure")
    
    return len(successful) > 0

def test_prompt_generation():
    """Test the prompt generation functionality"""
    
    print("\n🧪 Testing Prompt Generation")
    print("=" * 40)
    
    try:
        universal_prompt = UniversalAIPrompt()
        
        # Test different topics
        test_topics = [
            "Python Programming Basics",
            "Quantum Physics Fundamentals", 
            "Sustainable Business Practices"
        ]
        
        for topic in test_topics:
            print(f"\n📝 Testing prompt for: {topic}")
            
            prompt = universal_prompt.generate_universal_prompt(
                topic=topic,
                level="beginner",
                num_slides=5
            )
            
            print(f"✅ Prompt generated successfully")
            print(f"📏 Prompt length: {len(prompt)} characters")
            print(f"🔍 Contains subtopic types: {'Yes' if 'Subtopic Type Variety' in prompt else 'No'}")
            print(f"🎨 Contains NotebookLM style: {'Yes' if 'NOTEBOOKLM-STYLE' in prompt else 'No'}")
            
    except Exception as e:
        print(f"❌ Error testing prompt generation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Universal AI Prompt System Demo")
    
    # Test prompt generation first
    prompt_test_success = test_prompt_generation()
    
    if prompt_test_success:
        # Run main demo
        demo_success = demo_universal_prompt()
        
        if demo_success:
            print("\n🎉 All tests completed successfully!")
            print("📚 The Universal AI Prompt System is working correctly")
        else:
            print("\n⚠️ Demo completed with some issues")
    else:
        print("\n❌ Prompt generation test failed")
    
    print("\n📖 Check UNIVERSAL_AI_PROMPT_GUIDE.md for detailed usage instructions") 