#!/usr/bin/env python3
"""
Create Sun video using detailed manual content
"""

import json
import os
from video_generator import VideoGenerator

def create_manual_sun_video():
    """Create Sun video with detailed manual content"""
    
    print("🌞 Creating Sun Video with Detailed Content")
    print("=" * 50)
    
    # Detailed Sun content
    sun_content = {
        "topic": "The Sun: Our Star",
        "level": "beginner",
        "category": "space",
        "complexity": "moderate",
        "slides": [
            {
                "title": "Introduction to the Sun",
                "subtopics": ["Definition", "Core Concepts"],
                "bullets": [
                    "Our closest star",
                    "Center of solar system",
                    "Provides light and energy"
                ],
                "narration": "The Sun is our closest star and the center of our solar system. This massive ball of hydrogen and helium provides all the light and energy that sustains life on Earth. The Sun's immense gravity holds all the planets in orbit, and its energy drives weather patterns, ocean currents, and the entire food chain. Without the Sun, life as we know it would not exist. The Sun is so large that about 1.3 million Earths could fit inside it, and it contains 99.86% of all the mass in our solar system.",
                "examples": [
                    "Solar energy powers solar panels",
                    "Sunlight enables photosynthesis in plants"
                ],
                "visual_prompts": [
                    "Bright yellow sun with solar flares",
                    "Solar system diagram with Sun at center"
                ],
                "layout": "clean minimal, concept fade-in",
                "subtopic_type": "definition",
                "timing": 8
            },
            {
                "title": "Sun's Structure and Layers",
                "subtopics": ["Core", "Radiative Zone", "Convective Zone"],
                "bullets": [
                    "Nuclear fusion in core",
                    "Energy transfer through layers",
                    "Visible surface called photosphere"
                ],
                "narration": "The Sun has several distinct layers, each with unique properties and functions. At the very center lies the core, where nuclear fusion occurs at temperatures of 15 million degrees Celsius. This is where hydrogen atoms combine to form helium, releasing enormous amounts of energy. The radiative zone surrounds the core, where energy travels outward as electromagnetic radiation. Above that is the convective zone, where hot plasma rises and cooler material sinks, creating convection currents. The visible surface we see is called the photosphere, which appears as a bright disk in the sky.",
                "examples": [
                    "Nuclear fusion powers hydrogen bombs",
                    "Convection currents occur in boiling water"
                ],
                "visual_prompts": [
                    "Cross-section diagram of Sun layers",
                    "Nuclear fusion reaction illustration"
                ],
                "layout": "layered diagram, sequential reveals",
                "subtopic_type": "classification",
                "timing": 8
            },
            {
                "title": "Solar Activity and Phenomena",
                "subtopics": ["Sunspots", "Solar Flares", "Coronal Mass Ejections"],
                "bullets": [
                    "Dark spots on surface",
                    "Explosive energy releases",
                    "Magnetic field disturbances"
                ],
                "narration": "The Sun is far from static - it's a dynamic, active star with various phenomena occurring on its surface and in its atmosphere. Sunspots are dark regions on the photosphere that appear when magnetic field lines become twisted and concentrated. These spots are cooler than the surrounding areas, making them appear darker. Solar flares are sudden, intense bursts of radiation that occur when magnetic energy is released. These can affect Earth's atmosphere and disrupt communications. Coronal mass ejections are massive eruptions of plasma and magnetic field that can travel through space and impact Earth, causing geomagnetic storms.",
                "examples": [
                    "Aurora borealis caused by solar activity",
                    "Satellite communications affected by solar storms"
                ],
                "visual_prompts": [
                    "Sunspots on solar surface",
                    "Solar flare eruption sequence"
                ],
                "layout": "dynamic animations, energy burst effects",
                "subtopic_type": "process",
                "timing": 8
            },
            {
                "title": "Sun's Impact on Earth",
                "subtopics": ["Climate", "Technology", "Life"],
                "bullets": [
                    "Drives weather patterns",
                    "Affects satellite systems",
                    "Essential for all life"
                ],
                "narration": "The Sun's influence on Earth extends far beyond just providing light and warmth. It drives our planet's weather patterns through the heating of the atmosphere and oceans, creating wind currents and ocean circulation. The Sun's energy is essential for all life on Earth - plants use it for photosynthesis, which forms the base of the food chain. However, solar activity can also pose challenges to our technology. Solar storms can disrupt satellite communications, GPS systems, and even power grids. Understanding the Sun's behavior is crucial for protecting our technological infrastructure and understanding Earth's climate system.",
                "examples": [
                    "Solar panels convert sunlight to electricity",
                    "Weather satellites monitor solar radiation"
                ],
                "visual_prompts": [
                    "Earth receiving solar energy",
                    "Solar storm affecting satellites"
                ],
                "layout": "cause-effect diagram, impact visualization",
                "subtopic_type": "advantages_disadvantages",
                "timing": 8
            },
            {
                "title": "Future of Solar Research",
                "subtopics": ["Space Missions", "Solar Energy", "Climate Science"],
                "bullets": [
                    "Parker Solar Probe mission",
                    "Renewable energy development",
                    "Climate change understanding"
                ],
                "narration": "Our understanding of the Sun continues to evolve through advanced space missions and research. The Parker Solar Probe, launched in 2018, is the first spacecraft to fly through the Sun's corona, collecting unprecedented data about solar wind and magnetic fields. This mission helps us understand space weather and its effects on Earth. Solar energy technology is rapidly advancing, with more efficient solar panels and energy storage systems being developed. Understanding the Sun's role in climate change is crucial for predicting Earth's future climate patterns and developing strategies to address global warming.",
                "examples": [
                    "Parker Solar Probe discoveries",
                    "Solar energy becoming cheaper than fossil fuels"
                ],
                "visual_prompts": [
                    "Parker Solar Probe near Sun",
                    "Solar energy farm with panels"
                ],
                "layout": "timeline style, future projections",
                "subtopic_type": "timeline",
                "timing": 8
            }
        ]
    }
    
    try:
        # Initialize video generator
        video_generator = VideoGenerator()
        print("✅ Video generator initialized")
        
        # Save content
        with open("detailed_sun_content.json", 'w') as f:
            json.dump(sun_content, f, indent=2)
        print("💾 Detailed content saved")
        
        # Convert to script format
        script_lines = []
        for slide in sun_content.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video
        print("🎬 Generating detailed Sun video...")
        output_path = "detailed_sun_video.mp4"
        
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=8.0,
            width=1280,
            height=720,
            fps=30,
            topic="The Sun: Our Star"
        )
        
        print(f"✅ Detailed Sun video generated successfully!")
        print(f"📁 File: {video_path}")
        print(f"📏 Size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        print(f"⏱️ Duration: {len(sun_content.get('slides', [])) * 8} seconds")
        print(f"📊 Slides: {len(sun_content.get('slides', []))}")
        
        return video_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    video_path = create_manual_sun_video()
    
    if video_path:
        print(f"\n🎉 Detailed Sun video created successfully!")
        print(f"📹 Check '{video_path}' for your video with real content!")
        print("🌞 This video contains actual Sun information, not placeholder content!")
    else:
        print(f"\n❌ Failed to create video") 