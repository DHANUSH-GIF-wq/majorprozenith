import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyATAhnowhXOnFEjm1epqXVqjWtkWUYOSYk")
    
    # Application Configuration
    APP_TITLE = os.getenv("APP_TITLE", "ZenoZeno AI Chatbot")
    APP_ICON = os.getenv("APP_ICON", "🤖")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Video Generation Settings
    DEFAULT_VIDEO_WIDTH = int(os.getenv("DEFAULT_VIDEO_WIDTH", "1280"))
    DEFAULT_VIDEO_HEIGHT = int(os.getenv("DEFAULT_VIDEO_HEIGHT", "720"))
    DEFAULT_FPS = int(os.getenv("DEFAULT_FPS", "24"))
    MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "300"))
    
    # Text-to-Speech Settings
    TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "en")
    TTS_SLOW = os.getenv("TTS_SLOW", "false").lower() == "true"

    # Optional: ElevenLabs TTS
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True 