#!/usr/bin/env python3
"""
Test script to verify voice functionality in video generation
"""

import sys
import os
import tempfile

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from video_generator import VideoGenerator
from config import Config

def test_voice_generation():
    """Test that voice generation works properly"""
    print("🎤 Testing Voice Generation...")
    
    try:
        # Initialize video generator
        video_generator = VideoGenerator()
        
        # Test text
        test_text = "Hello, this is a test of the voice generation system. The ZenithIQ platform should now properly generate videos with audio narration."
        
        # Test text-to-speech
        print("📝 Testing text-to-speech...")
        audio_path = video_generator.text_to_speech(
            text=test_text,
            voice_gender="male",
            voice_name="Adam"
        )
        
        if os.path.exists(audio_path):
            print(f"✅ Audio generated successfully: {audio_path}")
            print(f"📊 File size: {os.path.getsize(audio_path)} bytes")
            
            # Clean up
            os.unlink(audio_path)
        else:
            print("❌ Audio file not created")
            return False
        
        # Test full video generation with voice
        print("\n🎬 Testing full video generation with voice...")
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video.close()
        
        video_path = video_generator.generate_video(
            text=test_text,
            duration=10,
            output_path=temp_video.name,
            voice_gender="male",
            voice_name="Adam"
        )
        
        if os.path.exists(video_path):
            print(f"✅ Video with voice generated successfully: {video_path}")
            print(f"📊 File size: {os.path.getsize(video_path)} bytes")
            
            # Clean up
            os.unlink(video_path)
            return True
        else:
            print("❌ Video file not created")
            return False
            
    except Exception as e:
        print(f"❌ Error during voice generation test: {e}")
        return False

def test_config():
    """Test configuration settings"""
    print("\n⚙️ Testing Configuration...")
    
    config = Config()
    print(f"TTS Language: {config.TTS_LANGUAGE}")
    print(f"TTS Slow: {config.TTS_SLOW}")
    print(f"ElevenLabs API Key: {'Set' if config.ELEVENLABS_API_KEY else 'Not set'}")
    
    return True

if __name__ == "__main__":
    print("🚀 ZenithIQ Voice Generation Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_config()
    
    # Test voice generation
    voice_ok = test_voice_generation()
    
    print("\n" + "=" * 50)
    if config_ok and voice_ok:
        print("✅ All tests passed! Voice generation should work properly.")
    else:
        print("❌ Some tests failed. Check the configuration and dependencies.")
    
    print("\n💡 To use high-quality voices, set ELEVENLABS_API_KEY in your .env file")
    print("📖 For free voice generation, the system will use Google Text-to-Speech (gTTS)") 