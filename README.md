# 🤖 ZenoZeno - AI Chatbot with Video Generator

A sophisticated AI chatbot application that combines Google's Gemini 2.5 Pro model with automated video generation capabilities. Create educational content, explanations, and tutorials with just a conversation!

## ✨ Features

### 🤖 AI Chatbot
- **Advanced AI Model**: Powered by Google's Gemini 2.5 Pro
- **Conversation History**: Persistent chat sessions with timestamps
- **Export Functionality**: Save conversations as JSON files
- **Error Handling**: Robust error handling with retry mechanisms
- **Connection Status**: Real-time service status monitoring

### 📹 Video Generator
- **Text-to-Speech**: Convert AI responses to natural speech
- **Customizable Videos**: Adjust duration, resolution, and frame rate
- **Background Images**: Automatic background image support with `testbg.jpeg`
- **Progress Tracking**: Real-time video generation progress
- **Download Support**: Direct video download functionality
- **Multiple Formats**: Support for various video settings

### 🎨 User Interface
- **Unified Interface**: Single application with tabbed interface
- **Modern Design**: Clean, responsive interface with custom styling
- **Sidebar Controls**: Easy access to all features and settings
- **Statistics Dashboard**: Track conversation metrics
- **Service Management**: Initialize and monitor AI services

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd zenozeno
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   APP_TITLE=ZenoZeno AI Chatbot
   APP_ICON=🤖
   DEBUG_MODE=false
   DEFAULT_VIDEO_WIDTH=1280
   DEFAULT_VIDEO_HEIGHT=720
   DEFAULT_FPS=1
   MAX_VIDEO_DURATION=300
   TTS_LANGUAGE=en
   TTS_SLOW=false
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
zenozeno/
├── app.py                    # Main unified application
├── config.py                 # Configuration management
├── ai_service.py             # AI model interactions
├── video_generator.py        # Video generation functionality
├── requirements.txt          # Python dependencies
├── setup.py                  # Setup script
├── README.md                 # Project documentation
└── .env                      # Environment variables (create this)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `APP_TITLE` | Application title | "ZenoZeno AI Chatbot" |
| `APP_ICON` | Application icon | "🤖" |
| `DEBUG_MODE` | Enable debug mode | false |
| `DEFAULT_VIDEO_WIDTH` | Default video width | 1280 |
| `DEFAULT_VIDEO_HEIGHT` | Default video height | 720 |
| `DEFAULT_FPS` | Default frames per second | 1 |
| `MAX_VIDEO_DURATION` | Maximum video duration (seconds) | 300 |
| `TTS_LANGUAGE` | Text-to-speech language | "en" |
| `TTS_SLOW` | Slow speech mode | false |

## 🎯 Usage

### Background Image Support
The video generator now automatically uses `testbg.jpeg` as the background image for all generated videos. This provides:

- **Professional Appearance**: Videos have a consistent, branded background
- **Text Readability**: Automatic overlay adjustments ensure text is clearly visible
- **Easy Customization**: Use `generator.set_default_background('path/to/image.jpg')` to change backgrounds
- **Fallback Support**: If no background image is available, videos use a solid color background

**Note**: Place your `testbg.jpeg` file in the project root directory for automatic detection.

### Quick Setup
1. Run the setup script: `python setup.py`
2. Start the application: `streamlit run app.py`
3. Initialize services in the sidebar
4. Start chatting and generating videos!

### Chat Interface
1. Click on the **💬 Chat** tab
2. Type your message and press Enter
3. Get AI responses with full conversation history
4. Export conversations or clear chat history

### Video Generation
1. Ask a question in the Chat tab to get an AI response
2. Switch to the **📹 Video Generator** tab
3. Configure video settings (duration, quality, etc.)
4. Click "Generate Video" to create and download the video

## 🛠️ Technical Details

### AI Service
- **Model**: Google Gemini 2.5 Pro
- **Retry Logic**: Exponential backoff with 3 attempts
- **Error Handling**: Comprehensive exception management
- **Connection Testing**: Service health monitoring

### Video Generation
- **Text-to-Speech**: Google TTS (gTTS)
- **Video Processing**: OpenCV
- **Format**: MP4 with H.264 codec
- **Customization**: Width, height, FPS, duration

### Security
- **API Key Management**: Environment variable storage
- **Configuration Validation**: Required field checking
- **Error Sanitization**: Safe error message display

## 🔍 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `GEMINI_API_KEY` is set in `.env`
   - Verify the API key is valid and has proper permissions

2. **Video Generation Fails**
   - Check OpenCV installation
   - Ensure sufficient disk space
   - Verify text-to-speech internet connection

3. **Import Errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

### Debug Mode
Enable debug mode in `.env`:
```env
DEBUG_MODE=true
```

## 🚀 Future Enhancements

- [ ] Multiple AI model support
- [ ] Advanced video templates
- [ ] Background music integration
- [ ] Subtitle generation
- [ ] Multi-language support
- [ ] User authentication
- [ ] Database integration
- [ ] REST API endpoints
- [ ] Docker containerization
- [ ] Cloud deployment support

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Made with ❤️ using Streamlit, Google Gemini, and OpenCV** 