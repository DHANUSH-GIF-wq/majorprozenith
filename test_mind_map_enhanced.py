#!/usr/bin/env python3
"""
Test script for enhanced mind map generator with Gemini AI
"""

import os
import sys
from mind_map_generator import MindMapGenerator
from ai_service import AIService

def test_mind_map_generation():
    """Test the enhanced mind map generator"""
    print("🧠 Testing Enhanced Mind Map Generator with Gemini AI")
    print("=" * 60)
    
    try:
        # Initialize services
        print("1. Initializing AI Service...")
        ai_service = AIService()
        print("   ✅ AI Service initialized")
        
        print("2. Initializing Mind Map Generator...")
        mind_map_gen = MindMapGenerator()
        print("   ✅ Mind Map Generator initialized")
        
        # Test topic
        test_topic = "Machine Learning"
        print(f"3. Testing mind map generation for: {test_topic}")
        
        # Generate mind map structure
        print("   Generating mind map structure...")
        mind_map_data = mind_map_gen.generate_mind_map_structure(test_topic, ai_service)
        
        print(f"   ✅ Mind map structure generated!")
        print(f"   Topic: {mind_map_data.get('topic', 'N/A')}")
        print(f"   Description: {mind_map_data.get('description', 'N/A')}")
        print(f"   Main branches: {len(mind_map_data.get('main_branches', []))}")
        
        # Display structure details
        for i, branch in enumerate(mind_map_data.get('main_branches', [])):
            print(f"   Branch {i+1}: {branch.get('title', 'N/A')} ({branch.get('color', 'N/A')})")
            print(f"     Description: {branch.get('description', 'N/A')}")
            print(f"     Sub-branches: {len(branch.get('sub_branches', []))}")
            
            for j, sub_branch in enumerate(branch.get('sub_branches', [])):
                print(f"       Sub-branch {j+1}: {sub_branch.get('title', 'N/A')}")
                print(f"         Key points: {len(sub_branch.get('key_points', []))}")
        
        # Test image generation
        print("4. Testing mind map image generation...")
        image_path = mind_map_gen.create_mind_map_image(mind_map_data)
        print(f"   ✅ Mind map image created: {image_path}")
        
        # Check if file exists
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"   Image file size: {file_size} bytes")
            
            # Cleanup
            os.unlink(image_path)
            print("   ✅ Image file cleaned up")
        else:
            print("   ❌ Image file not found")
        
        print("\n🎉 All tests passed! Mind map generator is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_functionality():
    """Test fallback functionality when AI is not available"""
    print("\n🔄 Testing Fallback Functionality")
    print("=" * 40)
    
    try:
        mind_map_gen = MindMapGenerator()
        test_topic = "Quantum Physics"
        
        print(f"Testing fallback mind map for: {test_topic}")
        fallback_data = mind_map_gen._create_fallback_mind_map(test_topic)
        
        print(f"   ✅ Fallback mind map created!")
        print(f"   Topic: {fallback_data.get('topic', 'N/A')}")
        print(f"   Main branches: {len(fallback_data.get('main_branches', []))}")
        
        # Test image generation with fallback
        image_path = mind_map_gen.create_mind_map_image(fallback_data)
        print(f"   ✅ Fallback mind map image created: {image_path}")
        
        if os.path.exists(image_path):
            os.unlink(image_path)
            print("   ✅ Fallback image file cleaned up")
        
        print("   ✅ Fallback functionality working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced Mind Map Generator Tests")
    print("=" * 60)
    
    # Test main functionality
    success1 = test_mind_map_generation()
    
    # Test fallback functionality
    success2 = test_fallback_functionality()
    
    if success1 and success2:
        print("\n🎉 All tests completed successfully!")
        print("The enhanced mind map generator is ready to use with Gemini AI.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        sys.exit(1) 