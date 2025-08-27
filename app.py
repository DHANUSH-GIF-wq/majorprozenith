import streamlit as st
import sys
import os
from datetime import datetime
import json
import tempfile

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService
from video_generator import VideoGenerator
from config import Config

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
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
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
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
    """Initialize AI and video generation services"""
    try:
        if st.session_state.ai_service is None:
            with st.spinner("Initializing AI service..."):
                st.session_state.ai_service = AIService()
        
        if st.session_state.video_generator is None:
            with st.spinner("Initializing video generator..."):
                st.session_state.video_generator = VideoGenerator()
        
        st.session_state.connection_status = "connected"
        st.success("✅ All services initialized successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {str(e)}")
        st.session_state.connection_status = "error"
        return False

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
    """Generate video with progress tracking"""
    try:
        with st.spinner("🎬 Generating video..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("Converting text to speech...")
            progress_bar.progress(25)
            
            # Generate video
            video_path = st.session_state.video_generator.generate_video(
                text=text,
                duration=duration,
                output_path=video_settings["output_path"],
                width=video_settings["width"],
                height=video_settings["height"],
                fps=video_settings["fps"]
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Video generated successfully!")
            
            return video_path
            
    except Exception as e:
        st.error(f"❌ Video generation failed: {str(e)}")
        return None

def chat_interface():
    """Chat interface tab"""
    st.markdown("### 💬 Chat with AI")
    
    # Display chat history
    if st.session_state.messages:
        display_chat_history()
    else:
        st.info("👋 Start a conversation by typing a message below!")
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Check if services are initialized
        if st.session_state.ai_service is None:
            st.error("❌ AI service not initialized. Please click 'Initialize Services' in the sidebar.")
            return
        
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display user message immediately
        with st.container():
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong><br>
                {user_input}
            </div>
            """, unsafe_allow_html=True)
        
        # Generate AI response
        with st.spinner("🤔 AI is thinking..."):
            try:
                response = st.session_state.ai_service.generate_response(user_input)
                st.session_state.last_response = response
                
                # Add AI response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Display AI response
                with st.container():
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>AI Assistant:</strong><br>
                        {response}
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                error_msg = f"❌ Error generating response: {str(e)}"
                st.markdown(f"""
                <div class="chat-message error-message">
                    {error_msg}
                </div>
                """, unsafe_allow_html=True)
                
                # Add error to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().isoformat()
                })

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
        st.markdown("#### 🎙️ Voice")
        colv1, colv2 = st.columns(2)
        with colv1:
            voice_gender = st.selectbox("Gender", ["male","female","neutral"], index=0)
        with colv2:
            voice_name = st.text_input("Voice name (optional)", placeholder="e.g., Adam, Rachel (ElevenLabs)")
        if st.button("🎬 Generate Video", use_container_width=True, key="generate_main_video"):
            if st.session_state.ai_service is None or st.session_state.video_generator is None:
                st.error("❌ Services not initialized. Click 'Initialize Services' in sidebar.")
            else:
                with st.spinner("Analyzing and generating video..."):
                    try:
                        # 1) Ingest content
                        extracted_texts = []
                        if topic.strip():
                            extracted_texts.append(topic.strip())
                            kb = st.session_state.ai_service.fetch_topic_knowledge(topic.strip())
                            if kb.get("summary"):
                                extracted_texts.append(kb.get("summary"))
                        for f in uploads or []:
                            name = f.name.lower()
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1])
                            tmp.write(f.read()); tmp.flush(); tmp.close()
                            if name.endswith(".pdf"):
                                try:
                                    from pypdf import PdfReader
                                    reader = PdfReader(tmp.name)
                                    for page in reader.pages:
                                        extracted_texts.append(page.extract_text() or "")
                                except Exception:
                                    pass
                            elif name.endswith(".docx"):
                                try:
                                    import docx
                                    doc = docx.Document(tmp.name)
                                    extracted_texts.append("\n".join([p.text for p in doc.paragraphs]))
                                except Exception:
                                    pass
                            elif name.endswith((".txt",)):
                                try:
                                    with open(tmp.name, 'r', errors='ignore') as fh:
                                        extracted_texts.append(fh.read())
                                except Exception:
                                    pass
                            elif name.endswith((".png",".jpg",".jpeg")):
                                try:
                                    import pytesseract
                                    import PIL.Image
                                    img = PIL.Image.open(tmp.name)
                                    extracted_texts.append(pytesseract.image_to_string(img))
                                except Exception:
                                    pass
                        merged_text = "\n\n".join([t for t in extracted_texts if t]).strip()
                        if not merged_text and not topic.strip():
                            st.warning("Please enter a topic or upload content.")
                            return
                        # 2) Ask AI for structured explainer directly (no visible script)
                        topic_text = topic.strip() or "Document"
                        data = st.session_state.ai_service.generate_explainer_structured(
                            topic=topic_text,
                            level=audience,
                            num_slides=6,
                            avoid_text=None
                        )
                        # refine with context
                        if merged_text:
                            data = st.session_state.ai_service.refine_structured_explainer(data, topic=topic.strip() or "Document", level=audience)
                        kb2 = st.session_state.ai_service.fetch_topic_knowledge(topic.strip() or "") if topic.strip() else {}
                        if kb2 and kb2.get("summary"):
                            data.setdefault("kb_images", kb2.get("images", []))
                        # 3) Generate video with clean, focused content
                        # Target total duration is automatically decided within 4–10 minutes
                        # do NOT repeat narration; rely on per-slide timing and audio padding for target duration
                        # 4) Render directly
                        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4"); temp_video.close()
                        
                        video_path = st.session_state.video_generator.generate_slideshow_video_structured(
                            structured=data,
                            image_paths=None,  # No custom background images
                            output_path=temp_video.name,
                            width=video_width2,
                            height=video_height2,
                            fps=fps2,
                            seconds_per_slide=8.0,
                            desired_total_seconds=None,
                            style=None,  # No reference video style
                            voice_gender=voice_gender,
                            voice_name=voice_name,
                            topic=topic_text,  # Pass topic for background selection
                        )
                        
                        # Save the path
                        st.session_state.explainer_video_path = video_path
                        st.success("✅ Video generated successfully!")
                        st.video(video_path)
                        
                        # Video actions in columns
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            with open(video_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ Download Video",
                                    data=file.read(),
                                    file_name=f"explanation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                        
                        with col2:
                            if st.button("🗑️ Delete Video", type="secondary", use_container_width=True, key="delete_generated_video"):
                                try:
                                    # Delete the video file
                                    if os.path.exists(video_path):
                                        os.unlink(video_path)
                                    # Clear the session state
                                    st.session_state.explainer_video_path = None
                                    st.success("✅ Video deleted successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to delete video: {e}")
                    except Exception as e:
                        st.error(f"❌ Failed to generate video: {e}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error during generation: {e}")

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

def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">🤖 ZenoZeno AI Chatbot + Video Generator</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Service status
        if st.session_state.connection_status == "connected":
            st.success("🟢 Services Connected")
        elif st.session_state.connection_status == "error":
            st.error("🔴 Service Error")
        else:
            st.info("🟡 Services Not Initialized")
        
        # Initialize services button
        if st.button("🔄 Initialize Services", use_container_width=True, key="initialize_services"):
            initialize_services()
        
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
    tab1, tab2 = st.tabs(["💬 Chat", "📹 Video Generator"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        video_generator_interface()

if __name__ == "__main__":
    main() 