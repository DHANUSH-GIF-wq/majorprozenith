#!/usr/bin/env python3
"""
Test script to verify Gemini API is working correctly
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService

def test_gemini_api():
    """Test the Gemini API connection"""
    print("🧪 Testing Gemini API Connection...")
    print("=" * 50)
    
    try:
        # Initialize AI service
        print("📡 Initializing AI Service...")
        ai_service = AIService()
        print("✅ AI Service initialized successfully")
        
        # Test basic response
        print("\n🤖 Testing basic response generation...")
        test_prompt = "Hello! Can you give me a brief explanation of artificial intelligence in one sentence?"
        response = ai_service.generate_response(test_prompt)
        
        if response and len(response) > 0:
            print("✅ Response generated successfully!")
            print(f"📝 Response: {response[:100]}...")
        else:
            print("❌ No response received")
            return False
        
        # Test connection
        print("\n🔗 Testing connection...")
        if ai_service.test_connection():
            print("✅ Connection test passed!")
        else:
            print("❌ Connection test failed!")
            return False
        
        # Get model info
        print("\n📊 Model Information:")
        model_info = ai_service.get_model_info()
        for key, value in model_info.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 All tests passed! Gemini API is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n🚀 ZenithIQ is ready to use!")
        print("Run 'streamlit run app.py' to start the application.")
    else:
        print("\n⚠️ Please check your configuration and try again.") 