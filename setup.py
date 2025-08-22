#!/usr/bin/env python3
"""
Setup script for ZenoZeno AI Chatbot
"""

import os
import sys

def create_env_file():
    """Create .env file with user input"""
    print("🤖 ZenoZeno AI Chatbot Setup")
    print("=" * 40)
    
    # Get API key
    api_key = input("Enter your Google Gemini API key: ").strip()
    if not api_key:
        print("❌ API key is required!")
        return False
    
    # Get other settings
    app_title = input("Application title (default: ZenoZeno AI Chatbot): ").strip() or "ZenoZeno AI Chatbot"
    debug_mode = input("Enable debug mode? (y/N): ").strip().lower() == 'y'
    
    # Create .env content
    env_content = f"""# Gemini API Configuration
GEMINI_API_KEY={api_key}

# Application Configuration
APP_TITLE={app_title}
APP_ICON=🤖
DEBUG_MODE={str(debug_mode).lower()}

# Video Generation Settings
DEFAULT_VIDEO_WIDTH=1280
DEFAULT_VIDEO_HEIGHT=720
DEFAULT_FPS=1
MAX_VIDEO_DURATION=300

# Text-to-Speech Settings
TTS_LANGUAGE=en
TTS_SLOW=false
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'google-generativeai',
        'gTTS',
        'opencv-python',
        'numpy',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up ZenoZeno AI Chatbot...")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return
    
    # Create .env file
    if create_env_file():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run the application: streamlit run app.py")
        print("2. Open your browser and start chatting!")
        print("3. Use the tabbed interface to switch between Chat and Video Generator")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 