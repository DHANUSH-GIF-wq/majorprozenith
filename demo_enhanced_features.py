#!/usr/bin/env python3
"""
Demonstration of Enhanced Video Generation Features
"""

import streamlit as st
from video_generator import VideoGenerator
from ai_service import AIService
import tempfile
import os

def main():
    st.title("🎬 Enhanced Video Generator Demo")
    st.markdown("""
    This demo showcases the improved video generation features:
    
    ✅ **Fixed repetitive explanations** - Better content flow and TTS timing
    ✅ **Topic-related backgrounds** - Intelligent background selection
    ✅ **Perfect content alignment** - Enhanced text positioning and styling
    """)
    
    # Initialize services
    try:
        video_generator = VideoGenerator()
        ai_service = AIService()
        st.success("✅ Services initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {e}")
        return
    
    st.divider()
    
    # Topic input
    topic = st.text_input("Enter a topic to explain:", 
                         placeholder="e.g., Artificial Intelligence, Quantum Computing, Climate Change")
    
    if st.button("🚀 Generate Enhanced Video", type="primary"):
        if not topic:
            st.warning("Please enter a topic!")
            return
        
        with st.spinner("🤖 Generating AI explanation..."):
            try:
                # Generate structured explainer
                data = ai_service.generate_explainer_structured(
                    topic=topic,
                    level="beginner",
                    num_slides=5
                )
                
                st.success("✅ AI explanation generated!")
                
                # Show the structure
                with st.expander("📋 Generated Content Structure"):
                    for i, slide in enumerate(data.get("slides", []), 1):
                        st.markdown(f"**Slide {i}: {slide.get('title', 'No title')}**")
                        for bullet in slide.get("bullets", []):
                            st.markdown(f"- {bullet}")
                        if slide.get("narration"):
                            st.markdown(f"*Narration: {slide['narration']}*")
                        st.divider()
                
            except Exception as e:
                st.error(f"❌ Failed to generate AI explanation: {e}")
                return
        
        # Video generation settings
        st.subheader("🎥 Video Settings")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            width = st.number_input("Width", min_value=640, max_value=1920, value=1280, step=160)
        with col2:
            height = st.number_input("Height", min_value=480, max_value=1080, value=720, step=120)
        with col3:
            fps = st.number_input("FPS", min_value=1, max_value=30, value=24, step=1)
        
        # Voice settings
        voice_gender = st.selectbox("Voice Gender", ["neutral", "male", "female"])
        
        if st.button("🎬 Generate Video with Enhanced Features"):
            with st.spinner("🎬 Generating enhanced video..."):
                try:
                    # Create temporary file for output
                    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                    temp_video.close()
                    
                    # Generate video with enhanced features
                    video_path = video_generator.generate_slideshow_video_structured(
                        structured=data,
                        output_path=temp_video.name,
                        width=width,
                        height=height,
                        fps=fps,
                        seconds_per_slide=8.0,
                        voice_gender=voice_gender,
                        topic=topic  # Pass topic for background selection
                    )
                    
                    st.success("✅ Enhanced video generated successfully!")
                    
                    # Display video
                    st.video(video_path)
                    
                    # Download button
                    with open(video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Download Enhanced Video",
                            data=file.read(),
                            file_name=f"enhanced_{topic.replace(' ', '_')}_{width}x{height}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                    
                    # Clean up
                    try:
                        os.unlink(video_path)
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"❌ Failed to generate video: {e}")
                    st.exception(e)
    
    st.divider()
    
    # Feature explanations
    st.subheader("🔧 Enhanced Features Explained")
    
    with st.expander("🎯 Content Flow Improvements"):
        st.markdown("""
        **What was fixed:**
        - Repetitive explanations and awkward breaks
        - Poor TTS timing and pacing
        - Unnatural speech patterns
        
        **How it's improved:**
        - Intelligent content restructuring
        - Natural pause insertion
        - Better sentence flow and transitions
        - Removed redundant slide numbering
        """)
    
    with st.expander("🖼️ Topic-Related Backgrounds"):
        st.markdown("""
        **New feature:**
        - Automatically selects relevant background images
        - Covers technology, science, education, business, health, art, nature, space
        - Intelligent topic matching and fallback system
        - Professional, contextually appropriate visuals
        """)
    
    with st.expander("📐 Perfect Content Alignment"):
        st.markdown("""
        **Enhanced layout:**
        - Centered titles with background highlights
        - Gradient overlays for better readability
        - Professional bullet point styling
        - Topic indicator at the top
        - Responsive text wrapping and positioning
        """)

if __name__ == "__main__":
    main()
