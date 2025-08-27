#!/usr/bin/env python3
"""
Test script for enhanced video generation features
"""

from video_generator import VideoGenerator
import os

def test_enhanced_video_generation():
    """Test the enhanced video generation with topic-related backgrounds"""
    
    # Initialize the video generator
    generator = VideoGenerator()
    
    # Test content
    test_text = """
    Artificial Intelligence is transforming our world in remarkable ways. 
    From self-driving cars to medical diagnosis, AI systems are becoming increasingly sophisticated. 
    Machine learning algorithms can now recognize patterns in data that humans might miss. 
    Deep learning networks process information in layers, similar to how our brains work. 
    The future holds even more exciting possibilities as AI continues to evolve.
    """
    
    # Test topic
    topic = "artificial intelligence"
    
    print("🎬 Testing Enhanced Video Generation...")
    print(f"📝 Content: {len(test_text)} characters")
    print(f"🏷️  Topic: {topic}")
    
    try:
        # Generate video with topic
        output_path = "test_enhanced_video.mp4"
        result = generator.generate_video(
            text=test_text,
            duration=15,
            output_path=output_path,
            topic=topic
        )
        
        if os.path.exists(result):
            print(f"✅ Video generated successfully: {result}")
            print(f"📁 File size: {os.path.getsize(result) / (1024*1024):.2f} MB")
        else:
            print("❌ Video file not found")
            
    except Exception as e:
        print(f"❌ Error generating video: {e}")

def test_topic_background_selection():
    """Test topic-related background selection"""
    
    generator = VideoGenerator()
    
    test_topics = [
        "technology",
        "science", 
        "education",
        "business",
        "health",
        "art",
        "nature",
        "space"
    ]
    
    print("\n🖼️  Testing Topic Background Selection...")
    
    for topic in test_topics:
        try:
            background = generator._get_topic_background(topic)
            if background is not None:
                print(f"✅ {topic}: Background loaded ({background.shape[1]}x{background.shape[0]})")
            else:
                print(f"⚠️  {topic}: Using fallback background")
        except Exception as e:
            print(f"❌ {topic}: Error - {e}")

def test_content_flow_improvement():
    """Test content flow improvement"""
    
    generator = VideoGenerator()
    
    test_texts = [
        "This is a test... with some breaks... and repetition...",
        "For example, this concept is important. However, there are challenges. Therefore, we need solutions.",
        "First, we start here. Next, we move forward. Finally, we complete the task."
    ]
    
    print("\n📝 Testing Content Flow Improvement...")
    
    for i, text in enumerate(test_texts, 1):
        improved = generator._improve_content_flow(text)
        print(f"\nTest {i}:")
        print(f"Original: {text}")
        print(f"Improved: {improved}")

if __name__ == "__main__":
    print("🚀 Enhanced Video Generator Test Suite")
    print("=" * 50)
    
    # Test content flow improvement
    test_content_flow_improvement()
    
    # Test topic background selection
    test_topic_background_selection()
    
    # Test video generation (uncomment to test actual video generation)
    # test_enhanced_video_generation()
    
    print("\n✨ Test suite completed!")
