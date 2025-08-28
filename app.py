import streamlit as st
import sys
import os
from datetime import datetime
import json
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService
from video_generator import VideoGenerator
from mind_map_generator import MindMapGenerator
from notes_generator import NotesGenerator
from quiz_generator import QuizGenerator
from study_planner import StudyPlanner
from config import Config

# Page configuration
st.set_page_config(
    page_title="ZenithIQ - AI Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
    }
    .user-message {
        background-color: #2c3e50;
        border-left: 4px solid #3498db;
        color: #ecf0f1;
    }
    .assistant-message {
        background-color: #34495e;
        border-left: 4px solid #9b59b6;
        color: #ecf0f1;
    }
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        color: #c62828;
    }
    .success-message {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        color: #2e7d32;
    }
    .video-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .feature-tabs {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f8f9fa;
        scroll-behavior: smooth;
        margin-bottom: 1rem;
    }
    .chat-input-container {
        background-color: transparent;
        padding: 0.5rem;
        border: none;
    }
    .typing-indicator {
        display: inline-block;
        animation: typing 1.5s infinite;
    }
    @keyframes typing {
        0%, 20% { opacity: 1; }
        50% { opacity: 0.5; }
        80%, 100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ai_service" not in st.session_state:
        st.session_state.ai_service = None
    if "video_generator" not in st.session_state:
        st.session_state.video_generator = None
    if "mind_map_generator" not in st.session_state:
        st.session_state.mind_map_generator = None
    if "notes_generator" not in st.session_state:
        st.session_state.notes_generator = None
    if "quiz_generator" not in st.session_state:
        st.session_state.quiz_generator = None
    if "study_planner" not in st.session_state:
        st.session_state.study_planner = None
    if "connection_status" not in st.session_state:
        st.session_state.connection_status = None
    if "last_response" not in st.session_state:
        st.session_state.last_response = None
    if "generated_video_path" not in st.session_state:
        st.session_state.generated_video_path = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Chat"
    if "explainer_script" not in st.session_state:
        st.session_state.explainer_script = ""
    if "explainer_video_path" not in st.session_state:
        st.session_state.explainer_video_path = None
    if "explainer_structured" not in st.session_state:
        st.session_state.explainer_structured = False
    if "explainer_structured_payload" not in st.session_state:
        st.session_state.explainer_structured_payload = None
    if "reference_video_path" not in st.session_state:
        st.session_state.reference_video_path = None

def initialize_services():
    """Initialize all AI services lazily (only when needed)"""
    try:
        # Don't initialize services immediately - just set them to None
        # They will be initialized when first used
        if st.session_state.ai_service is None:
            st.session_state.ai_service = None
        if st.session_state.video_generator is None:
            st.session_state.video_generator = None
        if st.session_state.mind_map_generator is None:
            st.session_state.mind_map_generator = None
        if st.session_state.notes_generator is None:
            st.session_state.notes_generator = None
        if st.session_state.quiz_generator is None:
            st.session_state.quiz_generator = None
        if st.session_state.study_planner is None:
            st.session_state.study_planner = None
        
        st.session_state.connection_status = "ready"
        return True
    except Exception as e:
        st.session_state.connection_status = "error"
        return False

def get_ai_service():
    """Get AI service instance, initializing if needed"""
    if st.session_state.ai_service is None:
        with st.spinner("Initializing AI Service..."):
            st.session_state.ai_service = AIService()
    return st.session_state.ai_service

def get_video_generator():
    """Get video generator instance, initializing if needed"""
    if st.session_state.video_generator is None:
        with st.spinner("Initializing Video Generator..."):
            st.session_state.video_generator = VideoGenerator()
    return st.session_state.video_generator

def get_mind_map_generator():
    """Get mind map generator instance, initializing if needed"""
    if st.session_state.mind_map_generator is None:
        with st.spinner("Initializing Mind Map Generator..."):
            st.session_state.mind_map_generator = MindMapGenerator()
    return st.session_state.mind_map_generator

def get_notes_generator():
    """Get notes generator instance, initializing if needed"""
    if st.session_state.notes_generator is None:
        with st.spinner("Initializing Notes Generator..."):
            st.session_state.notes_generator = NotesGenerator()
    return st.session_state.notes_generator

def get_quiz_generator():
    """Get quiz generator instance, initializing if needed"""
    if st.session_state.quiz_generator is None:
        with st.spinner("Initializing Quiz Generator..."):
            st.session_state.quiz_generator = QuizGenerator()
    return st.session_state.quiz_generator

def get_study_planner():
    """Get study planner instance, initializing if needed"""
    if st.session_state.study_planner is None:
        with st.spinner("Initializing Study Planner..."):
            st.session_state.study_planner = StudyPlanner()
    return st.session_state.study_planner

def display_chat_history():
    """Display chat history with improved styling"""
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>AI Assistant:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)

def export_conversation():
    """Export conversation to JSON file"""
    if st.session_state.messages:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        conversation_data = {
            "timestamp": timestamp,
            "messages": st.session_state.messages,
            "last_response": st.session_state.last_response
        }
        
        return json.dumps(conversation_data, indent=2), filename
    return None, None

def generate_video_with_progress(text, duration, video_settings):
    """Generate fast video with progress tracking"""
    try:
        with st.spinner("🎬 Generating fast video..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("Creating video frames...")
            progress_bar.progress(50)
            
            # Generate fast video
            video_generator = get_video_generator()
            video_path = video_generator.generate_fast_video(
                text=text,
                output_path=video_settings["output_path"],
                duration=min(10, duration)  # Max 10 seconds
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Fast video generated successfully!")
            
            return video_path
            
    except Exception as e:
        st.error(f"❌ Fast video generation failed: {str(e)}")
        return None

def chat_interface():
    """Chat interface tab with scrollable chat history"""
    st.markdown("### 💬 Chat with AI")
    
    # Create a container for the entire chat area
    chat_area = st.container()
    
    with chat_area:
        # Chat history container (fixed height)
        chat_history_container = st.container()
        with chat_history_container:
            st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
            
            # Display chat history in scrollable container
            if st.session_state.messages:
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>You:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message assistant-message">
                            <strong>AI Assistant:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("👋 Start a conversation by typing a message below!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input at the bottom (separate container)
        input_container = st.container()
        with input_container:
            user_input = st.chat_input("Type your message here...")
    
    # Handle user input
    if user_input:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display user message immediately
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            {user_input}
        </div>
        """, unsafe_allow_html=True)
        
        # Generate AI response instantly
        try:
            ai_service = get_ai_service()
            response = ai_service.generate_response(user_input)
            st.session_state.last_response = response
            
            # Add AI response to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Display AI response immediately
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>AI Assistant:</strong><br>
                {response}
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error generating response: {str(e)}")
            logger.error(f"Chat response generation failed: {e}")
        
        # Rerun to update the chat history
        st.rerun()

def video_generator_interface():
    """Video generator interface tab"""
    st.markdown("### 📹 Video Generator")
    
    with st.container():
        st.markdown("#### 🚀 Topic/Document → Video")
        st.markdown("""
        <div style='padding:10px;border-radius:10px;background:linear-gradient(135deg,#eef2f3,#e0ecff);border:1px solid #dfe7f3;'>
        Enter a topic or upload content. We’ll analyze it and directly generate a concise video explanation with narration and visuals.
        </div>
        """, unsafe_allow_html=True)
        colA, colB = st.columns([2,1])
        with colA:
            topic = st.text_input("Topic", placeholder="e.g., Black holes, Backpropagation, IPv6", help="Enter a clear, specific topic to explain")
            uploads = st.file_uploader(
                "Upload documents (PDF/DOCX/TXT/Images) - Optional",
                type=["pdf","docx","txt","png","jpg","jpeg"],
                accept_multiple_files=True,
                help="Upload additional content to enhance the explanation"
            )
        with colB:
            audience = st.selectbox("Audience Level", ["beginner","intermediate","advanced"], index=0, help="Choose the complexity level for your explanation")
        with st.expander("Advanced Video Settings"):
            video_width2 = st.number_input("Video Width", 640, 1920, Config.DEFAULT_VIDEO_WIDTH, 160, key="vw3")
            video_height2 = st.number_input("Video Height", 480, 1080, Config.DEFAULT_VIDEO_HEIGHT, 120, key="vh3")
            fps2 = st.number_input("Frames per Second", 1, 30, Config.DEFAULT_FPS, key="fps3")
        st.markdown("#### 🎙️ Voice Settings")
        st.markdown("""
        <div style='padding:8px;border-radius:8px;background:#e8f4fd;border:1px solid #b3d9ff;font-size:0.9em;'>
        💡 <strong>Voice Options:</strong><br>
        • <strong>ElevenLabs</strong> (Premium): Set ELEVENLABS_API_KEY in .env for high-quality voices<br>
        • <strong>gTTS</strong> (Free): Automatic fallback with Google Text-to-Speech
        </div>
        """, unsafe_allow_html=True)
        colv1, colv2 = st.columns(2)
        with colv1:
            voice_gender = st.selectbox("Gender", ["male","female","neutral"], index=0)
        with colv2:
            voice_name = st.text_input("Voice name (optional)", placeholder="e.g., Adam, Rachel (ElevenLabs)")
        col_gen1, col_gen2 = st.columns(2)
        with col_gen1:
            if st.button("🎬 Generate Video with Voice", use_container_width=True, key="generate_video_with_voice"):
                with st.spinner("Generating video with voice..."):
                    try:
                        # Create proper content for video
                        if topic.strip():
                            video_text = f"Topic: {topic.strip()}\n\n{topic.strip()} is an interesting subject that we can explore. This video provides a quick overview of the key concepts and important points to understand."
                        else:
                            video_text = "This is a video generated by ZenithIQ. The video provides a quick overview of the topic with key points and important information."
                        
                        # Generate video with audio using the proper method
                        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                        temp_video.close()
                        
                        video_generator = get_video_generator()
                        video_path = video_generator.generate_video(
                            text=video_text,
                            duration=15,  # 15 seconds for better content
                            output_path=temp_video.name,
                            voice_gender=voice_gender,
                            voice_name=voice_name
                        )
                        
                        # Save the path
                        st.session_state.explainer_video_path = video_path
                        st.success("✅ Video with voice generated successfully!")
                        st.video(video_path)
                        
                        # Video actions in columns
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            with open(video_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ Download Video with Voice",
                                    data=file.read(),
                                    file_name=f"video_with_voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                        
                        with col2:
                            if st.button("🔄 Generate Another", use_container_width=True):
                                st.session_state.explainer_video_path = None
                                st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Video generation with voice failed: {str(e)}")
                        logger.error(f"Video generation with voice failed: {e}")
        
        with col_gen2:
            if st.button("⚡ Generate Fast Video (No Voice)", use_container_width=True, key="generate_fast_video"):
                with st.spinner("Generating fast video..."):
                    try:
                        # Simple text processing
                        if topic.strip():
                            video_text = f"Topic: {topic.strip()}\n\n{topic.strip()} is an interesting subject that we can explore. This video provides a quick overview of the key concepts and important points to understand."
                        else:
                            video_text = "This is a fast video generated by ZenithIQ. The video provides a quick overview of the topic with key points and important information."
                        
                        # Generate fast video
                        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                        temp_video.close()
                        
                        video_generator = get_video_generator()
                        video_path = video_generator.generate_fast_video(
                            text=video_text,
                            output_path=temp_video.name,
                            duration=10  # Exactly 10 seconds
                        )
                        
                        # Save the path
                        st.session_state.explainer_video_path = video_path
                        st.success("✅ Fast video generated successfully in 10 seconds!")
                        st.video(video_path)
                        
                        # Video actions in columns
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            with open(video_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ Download Fast Video",
                                    data=file.read(),
                                    file_name=f"fast_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                        
                        with col2:
                            if st.button("🔄 Generate Another", use_container_width=True):
                                st.session_state.explainer_video_path = None
                                st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Fast video generation failed: {str(e)}")
                        logger.error(f"Fast video generation failed: {e}")

        # Display previously generated video if available
        if st.session_state.explainer_video_path:
            st.video(st.session_state.explainer_video_path)
            
            # Video actions in columns
            col1, col2 = st.columns([3, 1])
            
            with col1:
                with open(st.session_state.explainer_video_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Explainer Video",
                        data=file.read(),
                        file_name=f"explainer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🗑️ Delete Video", type="secondary", use_container_width=True, key="delete_existing_video"):
                    try:
                        # Delete the video file
                        if os.path.exists(st.session_state.explainer_video_path):
                            os.unlink(st.session_state.explainer_video_path)
                        # Clear the session state
                        st.session_state.explainer_video_path = None
                        st.success("✅ Video deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to delete video: {e}")

def mind_map_interface():
    """Mind map generator interface tab"""
    st.markdown("### 🗺️ Mind Map Generator")
    
    with st.container():
        st.markdown("#### 🧠 Visual Learning with Mind Maps")
        st.markdown("""
        <div style='padding:10px;border-radius:10px;background:linear-gradient(135deg,#eef2f3,#e0ecff);border:1px solid #dfe7f3;'>
        Create visual mind maps to organize concepts, ideas, and relationships. Perfect for brainstorming, studying, and understanding complex topics.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            topic = st.text_input("Topic for Mind Map", placeholder="e.g., Machine Learning, Quantum Physics, Business Strategy", help="Enter a topic to create a mind map")
        with col2:
            output_format = st.selectbox("Output Format", ["Image", "Video"], index=0, help="Choose output format")
        
        if st.button("🗺️ Generate Mind Map", use_container_width=True, key="generate_mind_map"):
            if not topic.strip():
                st.warning("Please enter a topic for the mind map.")
            else:
                with st.spinner("Creating mind map..."):
                    try:
                        if output_format == "Image":
                            # Generate mind map structure
                            mind_map_generator = get_mind_map_generator()
                            ai_service = get_ai_service()
                            mind_map_data = mind_map_generator.generate_mind_map_structure(
                                topic.strip(), ai_service
                            )
                            
                            # Create mind map image
                            image_path = mind_map_generator.create_mind_map_image(mind_map_data)
                            
                            # Display image
                            st.image(image_path, caption=f"Mind Map: {topic}", use_column_width=True)
                            
                            # Download button
                            with open(image_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ Download Mind Map Image",
                                    data=file.read(),
                                    file_name=f"mind_map_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                            
                            # Cleanup
                            if os.path.exists(image_path):
                                os.unlink(image_path)
                        
                        else:  # Video format
                            # Generate mind map video
                            video_path = mind_map_generator.generate_mind_map_video(
                                topic.strip(), ai_service
                            )
                            
                            # Display video
                            st.video(video_path)
                            
                            # Download button
                            with open(video_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ Download Mind Map Video",
                                    data=file.read(),
                                    file_name=f"mind_map_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                            
                            # Cleanup
                            if os.path.exists(video_path):
                                os.unlink(video_path)
                        
                        st.success("✅ Mind map generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to generate mind map: {e}")

def notes_interface():
    """Study notes generator interface tab"""
    st.markdown("### 📝 Study Notes Generator")
    
    with st.container():
        st.markdown("#### 📚 Comprehensive Study Materials")
        st.markdown("""
        <div style='padding:10px;border-radius:10px;background:linear-gradient(135deg,#eef2f3,#e0ecff);border:1px solid #dfe7f3;'>
        Generate comprehensive study notes, summaries, flashcards, and study guides. Perfect for exam preparation and learning.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            topic = st.text_input("Topic for Notes", placeholder="e.g., Calculus, Psychology, Programming", help="Enter a topic to generate study notes")
        with col2:
            note_type = st.selectbox("Note Type", ["comprehensive", "summary", "flashcards", "study_guide"], index=0, help="Choose the type of notes to generate")
        
        if st.button("📝 Generate Notes", use_container_width=True, key="generate_notes"):
            if not topic.strip():
                st.warning("Please enter a topic for the notes.")
            else:
                with st.spinner("Generating study notes..."):
                    try:
                        # Generate notes
                        notes_generator = get_notes_generator()
                        ai_service = get_ai_service()
                        notes_data = notes_generator.generate_notes(
                            topic.strip(), ai_service, note_type
                        )
                        
                        # Display notes
                        st.markdown(f"## 📝 {notes_data.get('topic', topic)} - {note_type.title()}")
                        st.markdown(f"**Generated:** {notes_data.get('generated_at', 'Unknown')}")
                        
                        if note_type == "comprehensive":
                            for section in notes_data.get('sections', []):
                                st.markdown(f"### {section.get('title', 'Section')}")
                                st.write(section.get('content', ''))
                                
                                if section.get('key_points'):
                                    st.markdown("**Key Points:**")
                                    for point in section['key_points']:
                                        st.markdown(f"- {point}")
                                
                                if section.get('examples'):
                                    st.markdown("**Examples:**")
                                    for example in section['examples']:
                                        st.markdown(f"- {example}")
                                
                                if section.get('tips'):
                                    st.markdown("**Tips:**")
                                    for tip in section['tips']:
                                        st.markdown(f"- {tip}")
                        
                        elif note_type == "summary":
                            st.markdown(f"**Overview:** {notes_data.get('overview', '')}")
                            
                            if notes_data.get('key_concepts'):
                                st.markdown("**Key Concepts:**")
                                for concept in notes_data['key_concepts']:
                                    st.markdown(f"- {concept}")
                            
                            if notes_data.get('definitions'):
                                st.markdown("**Definitions:**")
                                for definition in notes_data['definitions']:
                                    st.markdown(f"- **{definition.get('term', '')}**: {definition.get('definition', '')}")
                        
                        elif note_type == "flashcards":
                            st.markdown("**Flashcards:**")
                            for i, card in enumerate(notes_data.get('flashcards', []), 1):
                                with st.expander(f"Card {i}: {card.get('front', '')}"):
                                    st.markdown(f"**Answer:** {card.get('back', '')}")
                                    st.markdown(f"**Category:** {card.get('category', '')}")
                        
                        elif note_type == "study_guide":
                            if notes_data.get('learning_objectives'):
                                st.markdown("**Learning Objectives:**")
                                for objective in notes_data['learning_objectives']:
                                    st.markdown(f"- {objective}")
                            
                            if notes_data.get('learning_path'):
                                st.markdown("**Learning Path:**")
                                for step in notes_data['learning_path']:
                                    st.markdown(f"### Step {step.get('step', '')}: {step.get('title', '')}")
                                    st.write(step.get('description', ''))
                                    st.markdown(f"**Duration:** {step.get('duration', '')}")
                        
                        # Export to Markdown
                        markdown_path = st.session_state.notes_generator.export_notes_to_markdown(notes_data)
                        with open(markdown_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download Notes (Markdown)",
                                data=file.read(),
                                file_name=f"notes_{topic.replace(' ', '_')}_{note_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                        
                        # Cleanup
                        if os.path.exists(markdown_path):
                            os.unlink(markdown_path)
                        
                        st.success("✅ Study notes generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to generate notes: {e}")

def quiz_interface():
    """Quiz generator interface tab"""
    st.markdown("### ❓ Quiz Generator")
    
    with st.container():
        st.markdown("#### 🧠 Interactive Learning Assessment")
        st.markdown("""
        <div style='padding:10px;border-radius:10px;background:linear-gradient(135deg,#eef2f3,#e0ecff);border:1px solid #dfe7f3;'>
        Create interactive quizzes to test knowledge and understanding. Multiple question types and difficulty levels available.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            topic = st.text_input("Topic for Quiz", placeholder="e.g., Mathematics, Science, History", help="Enter a topic to create a quiz")
        with col2:
            quiz_type = st.selectbox("Quiz Type", ["multiple_choice", "true_false", "fill_blank", "matching", "essay"], index=0, help="Choose quiz type")
        with col3:
            num_questions = st.number_input("Number of Questions", min_value=5, max_value=50, value=10, help="Number of questions in the quiz")
        
        col4, col5 = st.columns([1, 1])
        with col4:
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1, help="Quiz difficulty level")
        
        if st.button("❓ Generate Quiz", use_container_width=True, key="generate_quiz"):
            if not topic.strip():
                st.warning("Please enter a topic for the quiz.")
            else:
                with st.spinner("Generating quiz..."):
                    try:
                        # Generate quiz
                        quiz_generator = get_quiz_generator()
                        ai_service = get_ai_service()
                        quiz_data = quiz_generator.generate_quiz(
                            topic.strip(), ai_service, quiz_type, num_questions, difficulty
                        )
                        
                        # Store quiz data in session state
                        st.session_state.current_quiz = quiz_data
                        st.session_state.quiz_answers = {}
                        
                        st.success("✅ Quiz generated successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Failed to generate quiz: {e}")
        
        # Display quiz if available
        if hasattr(st.session_state, 'current_quiz') and st.session_state.current_quiz:
            quiz_data = st.session_state.current_quiz
            
            st.markdown(f"## ❓ {quiz_data.get('topic', 'Quiz')} - {quiz_data.get('quiz_type', 'Quiz').title()}")
            st.markdown(f"**Difficulty:** {quiz_data.get('difficulty', 'Medium')} | **Questions:** {quiz_data.get('num_questions', 0)}")
            
            if quiz_data.get('instructions'):
                st.markdown(f"**Instructions:** {quiz_data['instructions']}")
            
            # Quiz interface
            with st.form("quiz_form"):
                if quiz_data.get('quiz_type') == 'multiple_choice':
                    for i, question in enumerate(quiz_data.get('questions', [])):
                        st.markdown(f"**{i+1}.** {question.get('question', '')}")
                        options = question.get('options', [])
                        answer = st.radio(f"Answer for question {i+1}", options, key=f"q{i}")
                        st.session_state.quiz_answers[str(i)] = answer
                
                elif quiz_data.get('quiz_type') == 'true_false':
                    for i, question in enumerate(quiz_data.get('questions', [])):
                        st.markdown(f"**{i+1}.** {question.get('statement', '')}")
                        answer = st.radio(f"Answer for question {i+1}", ["True", "False"], key=f"q{i}")
                        st.session_state.quiz_answers[str(i)] = answer == "True"
                
                elif quiz_data.get('quiz_type') == 'fill_blank':
                    for i, question in enumerate(quiz_data.get('questions', [])):
                        st.markdown(f"**{i+1}.** {question.get('sentence', '')}")
                        answer = st.text_input(f"Answer for question {i+1}", key=f"q{i}")
                        st.session_state.quiz_answers[str(i)] = answer
                
                elif quiz_data.get('quiz_type') == 'matching':
                    items = quiz_data.get('items', [])
                    st.markdown("Match each term with its definition:")
                    
                    # Shuffle items for quiz
                    import random
                    shuffled_items = items.copy()
                    random.shuffle(shuffled_items)
                    
                    for i, item in enumerate(shuffled_items):
                        st.markdown(f"**{i+1}.** {item.get('term', '')}")
                    
                    st.markdown("**Definitions:**")
                    definitions = [item.get('definition', '') for item in items]
                    random.shuffle(definitions)
                    
                    for i, definition in enumerate(definitions):
                        st.markdown(f"**{chr(65+i)}.** {definition}")
                    
                    # Simple matching interface
                    for i in range(len(items)):
                        answer = st.text_input(f"Match for term {i+1} (enter A, B, C, etc.)", key=f"q{i}")
                        st.session_state.quiz_answers[str(i)] = answer
                
                elif quiz_data.get('quiz_type') == 'essay':
                    for i, question in enumerate(quiz_data.get('questions', [])):
                        st.markdown(f"**{i+1}.** {question.get('prompt', '')}")
                        st.markdown(f"**Suggested Length:** {question.get('suggested_length', '')}")
                        answer = st.text_area(f"Answer for question {i+1}", key=f"q{i}", height=150)
                        st.session_state.quiz_answers[str(i)] = answer
                
                submitted = st.form_submit_button("📊 Grade Quiz", use_container_width=True)
                
                if submitted:
                    try:
                        # Grade the quiz
                        results = quiz_generator.grade_quiz(quiz_data, st.session_state.quiz_answers)
                        
                        # Display results
                        st.markdown("## 📊 Quiz Results")
                        st.markdown(f"**Score:** {results.get('score_percentage', 0)}%")
                        st.markdown(f"**Correct Answers:** {results.get('correct_answers', 0)}/{results.get('total_questions', 0)}")
                        st.markdown(f"**Status:** {'✅ Passed' if results.get('passed', False) else '❌ Failed'}")
                        st.markdown(f"**Feedback:** {results.get('feedback', '')}")
                        
                        # Detailed results
                        with st.expander("📋 Detailed Results"):
                            for i, result in enumerate(results.get('detailed_results', []), 1):
                                status = "✅" if result.get('correct', False) else "❌"
                                question_text = result.get('question', result.get('statement', result.get('sentence', '')))
                                st.markdown(f"**{i}.** {status} {question_text}")
                                if not result.get('correct', False):
                                    st.markdown(f"   Your answer: {result.get('user_answer', '')}")
                                    st.markdown(f"   Correct answer: {result.get('correct_answer', '')}")
                                st.markdown(f"   Explanation: {result.get('explanation', '')}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to grade quiz: {e}")
            
            # Export quiz
            col1, col2 = st.columns([1, 1])
            with col1:
                markdown_path = quiz_generator.export_quiz_to_markdown(quiz_data)
                with open(markdown_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Quiz (Markdown)",
                        data=file.read(),
                        file_name=f"quiz_{topic.replace(' ', '_')}_{quiz_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🔄 New Quiz", use_container_width=True):
                    st.session_state.current_quiz = None
                    st.session_state.quiz_answers = {}
                    st.rerun()

def study_planner_interface():
    """Study planner interface tab"""
    st.markdown("### 📅 Study Planner")
    
    with st.container():
        st.markdown("#### 🎯 Personalized Learning Plans")
        st.markdown("""
        <div style='padding:10px;border-radius:10px;background:linear-gradient(135deg,#eef2f3,#e0ecff);border:1px solid #dfe7f3;'>
        Create personalized study plans with schedules, objectives, and progress tracking. Perfect for exam preparation and long-term learning.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            topic = st.text_input("Topic for Study Plan", placeholder="e.g., Advanced Mathematics, Programming, Language Learning", help="Enter a topic to create a study plan")
        with col2:
            study_duration = st.number_input("Study Duration (days)", min_value=1, max_value=90, value=7, help="Number of days to study")
        with col3:
            hours_per_day = st.number_input("Hours per Day", min_value=1, max_value=8, value=2, help="Hours to study each day")
        
        col4, col5 = st.columns([1, 1])
        with col4:
            difficulty = st.selectbox("Difficulty Level", ["easy", "medium", "hard"], index=1, help="Study difficulty level")
        with col5:
            study_method = st.selectbox("Study Method", ["pomodoro", "traditional", "intensive", "casual"], index=0, help="Study technique to use")
        
        if st.button("📅 Generate Study Plan", use_container_width=True, key="generate_study_plan"):
            if not topic.strip():
                st.warning("Please enter a topic for the study plan.")
            else:
                with st.spinner("Creating study plan..."):
                    try:
                        # Generate study plan
                        study_planner = get_study_planner()
                        ai_service = get_ai_service()
                        study_plan = study_planner.generate_study_plan(
                            topic.strip(), ai_service, study_duration, hours_per_day, difficulty, study_method
                        )
                        
                        # Store study plan in session state
                        st.session_state.current_study_plan = study_plan
                        
                        st.success("✅ Study plan generated successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Failed to generate study plan: {e}")
        
        # Display study plan if available
        if hasattr(st.session_state, 'current_study_plan') and st.session_state.current_study_plan:
            plan = st.session_state.current_study_plan
            
            st.markdown(f"## 📅 Study Plan: {plan.get('topic', 'Topic')}")
            st.markdown(f"**Duration:** {plan.get('study_duration', 0)} days | **Hours per Day:** {plan.get('hours_per_day', 0)} | **Method:** {plan.get('study_method', '').title()}")
            
            # Progress tracking
            progress = plan.get('progress_tracking', {})
            st.markdown("### 📊 Progress Tracking")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Units", progress.get('total_units', 0))
            with col2:
                st.metric("Completed Units", progress.get('completed_units', 0))
            with col3:
                st.metric("Total Hours", progress.get('total_hours', 0))
            with col4:
                st.metric("Progress", f"{progress.get('progress_percentage', 0):.1f}%")
            
            # Learning objectives
            with st.expander("🎯 Learning Objectives"):
                for i, objective in enumerate(plan.get('objectives', []), 1):
                    st.markdown(f"**{i}.** {objective.get('objective', '')}")
                    st.markdown(f"   - Category: {objective.get('category', '')}")
                    st.markdown(f"   - Difficulty: {objective.get('difficulty', '')}")
                    st.markdown(f"   - Timeframe: {objective.get('timeframe', '')}")
            
            # Topic breakdown
            with st.expander("📚 Topic Breakdown"):
                for i, unit in enumerate(plan.get('topic_breakdown', []), 1):
                    st.markdown(f"**{i}.** {unit.get('title', '')}")
                    st.write(unit.get('description', ''))
                    st.markdown(f"   - Hours: {unit.get('estimated_hours', 0)}")
                    st.markdown(f"   - Difficulty: {unit.get('difficulty', '')}")
            
            # Study schedule
            with st.expander("📅 Study Schedule"):
                schedule = plan.get('schedule', {})
                for daily in schedule.get('daily_schedules', []):
                    st.markdown(f"### Day {daily.get('day', '')} - {daily.get('day_of_week', '')}")
                    for session in daily.get('sessions', []):
                        st.markdown(f"- **{session.get('unit', '')}** ({session.get('duration', 0)} hours)")
            
            # Study tips
            with st.expander("💡 Study Tips"):
                for tip in plan.get('study_tips', []):
                    st.markdown(f"- {tip}")
            
            # Resources
            with st.expander("📖 Study Resources"):
                for resource in plan.get('resources', []):
                    st.markdown(f"**{resource.get('title', '')}**")
                    st.markdown(f"- Type: {resource.get('type', '')}")
                    st.markdown(f"- Description: {resource.get('description', '')}")
                    if resource.get('url'):
                        st.markdown(f"- URL: {resource.get('url', '')}")
            
            # Progress update
            st.markdown("### 📝 Update Progress")
            with st.form("progress_update"):
                completed_units = st.multiselect(
                    "Completed Units",
                    [unit.get('title', '') for unit in plan.get('topic_breakdown', [])],
                    help="Select units you have completed"
                )
                completed_hours = st.number_input("Hours Studied Today", min_value=0.0, value=0.0, step=0.5)
                notes = st.text_area("Notes", placeholder="Any notes about your study session...")
                
                if st.form_submit_button("📊 Update Progress"):
                    try:
                        # Update progress
                        updated_plan = study_planner.update_progress(
                            plan, completed_units, completed_hours, notes
                        )
                        st.session_state.current_study_plan = updated_plan
                        st.success("✅ Progress updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update progress: {e}")
            
            # Export study plan
            col1, col2 = st.columns([1, 1])
            with col1:
                markdown_path = study_planner.export_study_plan_to_markdown(plan)
                with open(markdown_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Study Plan (Markdown)",
                        data=file.read(),
                        file_name=f"study_plan_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🔄 New Study Plan", use_container_width=True):
                    st.session_state.current_study_plan = None
                    st.rerun()

def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">🤖 ZenithIQ - AI-Powered Learning Platform</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize services (lazy loading)
    initialize_services()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Service status
        if st.session_state.connection_status == "ready":
            st.success("🟢 Ready to Use")
        elif st.session_state.connection_status == "error":
            st.error("🔴 Service Error")
        else:
            st.info("🟡 Initializing...")
        
        st.divider()
        
        # Export conversation
        if st.session_state.messages:
            conversation_json, filename = export_conversation()
            if conversation_json:
                st.download_button(
                    label="📥 Export Conversation",
                    data=conversation_json,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation", use_container_width=True, key="clear_conversation"):
            st.session_state.messages = []
            st.session_state.last_response = None
            st.session_state.generated_video_path = None
            st.rerun()
        
        st.divider()
        
        # App info
        st.markdown("### 📊 Stats")
        st.metric("Messages", len(st.session_state.messages))
        
        if st.session_state.messages:
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            st.metric("User Messages", user_messages)
            st.metric("AI Responses", ai_messages)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💬 Chat", 
        "📹 Video Generator", 
        "🗺️ Mind Maps", 
        "📝 Study Notes", 
        "❓ Quizzes", 
        "📅 Study Planner"
    ])
    
    with tab1:
        chat_interface()
    
    with tab2:
        video_generator_interface()
    
    with tab3:
        mind_map_interface()
    
    with tab4:
        notes_interface()
    
    with tab5:
        quiz_interface()
    
    with tab6:
        study_planner_interface()

if __name__ == "__main__":
    main() 