#!/usr/bin/env python3
"""
ZenithIQ Startup Script
Launch the AI-Powered Learning Platform
"""

import subprocess
import sys
import os

def start_zenithiq():
    """Start the ZenithIQ application"""
    print("🎓 Starting ZenithIQ - AI-Powered Learning Platform")
    print("=" * 60)
    print("Loading all services...")
    print("📡 AI Service (Gemini 2.5 Pro)")
    print("📹 Video Generator")
    print("🗺️ Mind Map Generator")
    print("📝 Study Notes Generator")
    print("❓ Quiz Generator")
    print("📅 Study Planner")
    print("=" * 60)
    print("🚀 Launching ZenithIQ...")
    print("🌐 Opening in your default browser...")
    print("=" * 60)
    
    try:
        # Start Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"], check=True)
    except KeyboardInterrupt:
        print("\n👋 ZenithIQ stopped by user")
    except Exception as e:
        print(f"❌ Error starting ZenithIQ: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    start_zenithiq() 