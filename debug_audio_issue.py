#!/usr/bin/env python3
"""
Debug script to identify and fix audio generation issues
"""

import os
import tempfile
from video_generator import VideoGenerator
from ai_service import AIService
import subprocess

def test_tts_generation():
    """Test TTS generation step by step"""
    
    print("🔍 Testing TTS Generation...")
    
    try:
        # Initialize services
        video_generator = VideoGenerator()
        ai_service = AIService()
        print("✅ Services initialized successfully!")
        
        # Test text
        test_text = "This is a test of the text to speech system. It should generate clear audio."
        print(f"📝 Test text: {test_text}")
        
        # Test TTS generation
        print("\n🎤 Testing TTS generation...")
        audio_path = video_generator.text_to_speech(test_text)
        
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"✅ Audio file generated: {audio_path}")
            print(f"📁 File size: {file_size} bytes")
            
            # Check if file is not empty
            if file_size > 100:
                print("✅ Audio file has content")
            else:
                print("❌ Audio file is too small - may be empty")
        else:
            print("❌ Audio file not created")
            return False
            
    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        return False
    
    return True

def test_ffmpeg_availability():
    """Test if ffmpeg is available and working"""
    
    print("\n🔍 Testing FFmpeg availability...")
    
    try:
        # Check if imageio-ffmpeg is available
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"✅ FFmpeg found: {ffmpeg_exe}")
        
        # Test ffmpeg command
        result = subprocess.run([ffmpeg_exe, "-version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is working correctly")
            return True
        else:
            print(f"❌ FFmpeg command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ FFmpeg test failed: {e}")
        return False

def test_audio_merging():
    """Test audio merging with ffmpeg"""
    
    print("\n🔍 Testing audio merging...")
    
    try:
        # Create a simple test video (1 second, black frame)
        import cv2
        import numpy as np
        
        # Create test video
        test_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        test_video.close()
        
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(test_video.name, fourcc, 24, (640, 480))
        
        # Write 24 frames (1 second at 24fps)
        for _ in range(24):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            writer.write(frame)
        writer.release()
        
        # Create test audio
        video_generator = VideoGenerator()
        test_text = "This is a test audio for merging."
        audio_path = video_generator.text_to_speech(test_text)
        
        # Test merging
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_path.close()
        
        cmd = [
            ffmpeg_exe, "-y",
            "-i", test_video.name,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            output_path.name
        ]
        
        print(f"🔄 Running FFmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            if os.path.exists(output_path.name):
                file_size = os.path.getsize(output_path.name)
                print(f"✅ Audio merging successful: {output_path.name}")
                print(f"📁 Output file size: {file_size} bytes")
                
                # Cleanup
                os.unlink(test_video.name)
                os.unlink(audio_path)
                os.unlink(output_path.name)
                return True
            else:
                print("❌ Output file not created")
                return False
        else:
            print(f"❌ FFmpeg merging failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Audio merging test failed: {e}")
        return False

def check_environment():
    """Check environment and dependencies"""
    
    print("\n🔍 Checking environment...")
    
    # Check Python packages
    packages = [
        "gtts", "opencv-python", "numpy", "imageio-ffmpeg", "elevenlabs"
    ]
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is NOT available")
    
    # Check environment variables
    print("\n🔍 Checking environment variables...")
    
    env_vars = [
        "GEMINI_API_KEY",
        "ELEVENLABS_API_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "")
        if value:
            print(f"✅ {var} is set ({value[:10]}...)")
        else:
            print(f"⚠️  {var} is not set")

def main():
    """Main diagnostic function"""
    
    print("🚀 Audio Issue Diagnostic Tool")
    print("=" * 50)
    
    # Check environment
    check_environment()
    
    # Test TTS generation
    tts_ok = test_tts_generation()
    
    # Test FFmpeg availability
    ffmpeg_ok = test_ffmpeg_availability()
    
    # Test audio merging
    merging_ok = test_audio_merging()
    
    print("\n" + "=" * 50)
    print("📊 Diagnostic Results:")
    print(f"  TTS Generation: {'✅ OK' if tts_ok else '❌ FAILED'}")
    print(f"  FFmpeg Availability: {'✅ OK' if ffmpeg_ok else '❌ FAILED'}")
    print(f"  Audio Merging: {'✅ OK' if merging_ok else '❌ FAILED'}")
    
    if tts_ok and ffmpeg_ok and merging_ok:
        print("\n✨ All audio components are working correctly!")
        print("   The issue might be in the main video generation pipeline.")
    else:
        print("\n⚠️  Some audio components have issues.")
        print("   Please fix the failed components above.")
    
    print("\n💡 To run the app:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main()
