#!/usr/bin/env python3
"""
Create Sun video with REAL facts and content
"""

import json
import os
from video_generator import VideoGenerator

def create_real_sun_facts_video():
    """Create Sun video with actual facts and real content"""
    
    print("🌞 Creating Sun Video with REAL Facts")
    print("=" * 50)
    
    # REAL Sun content with actual facts
    real_sun_content = {
        "topic": "The Sun: Our Star",
        "level": "beginner",
        "category": "space",
        "slides": [
            {
                "title": "What is the Sun?",
                "bullets": [
                    "Massive ball of hydrogen and helium",
                    "99.86% of solar system mass",
                    "1.3 million Earths could fit inside"
                ],
                "narration": "The Sun is a massive ball of hydrogen and helium gas that contains 99.86% of all the mass in our solar system. It's so enormous that about 1.3 million Earths could fit inside it. The Sun's surface temperature reaches 5,500 degrees Celsius, while its core burns at 15 million degrees Celsius. This incredible heat and pressure cause hydrogen atoms to fuse together, creating helium and releasing enormous amounts of energy that powers our entire solar system."
            },
            {
                "title": "Sun's Structure",
                "bullets": [
                    "Core: Nuclear fusion at 15 million°C",
                    "Radiative zone: Energy transfer",
                    "Convective zone: Hot plasma movement",
                    "Photosphere: Visible surface"
                ],
                "narration": "The Sun has four main layers. At the center is the core, where nuclear fusion occurs at temperatures of 15 million degrees Celsius. Here, hydrogen atoms combine to form helium, releasing energy. The radiative zone surrounds the core, where energy travels outward as electromagnetic radiation. Above that is the convective zone, where hot plasma rises and cooler material sinks in convection currents. The visible surface we see is called the photosphere, which appears as a bright yellow disk in the sky."
            },
            {
                "title": "Solar Activity",
                "bullets": [
                    "Sunspots: Dark, cooler regions",
                    "Solar flares: Explosive energy bursts",
                    "Coronal mass ejections: Plasma eruptions"
                ],
                "narration": "The Sun is incredibly active and dynamic. Sunspots are dark regions on the photosphere that appear when magnetic field lines become twisted and concentrated. These spots are cooler than the surrounding areas, making them appear darker. Solar flares are sudden, intense bursts of radiation that occur when magnetic energy is released. These can affect Earth's atmosphere and disrupt communications. Coronal mass ejections are massive eruptions of plasma and magnetic field that can travel through space and impact Earth, causing geomagnetic storms and beautiful auroras."
            },
            {
                "title": "Sun's Impact on Earth",
                "bullets": [
                    "Drives weather and climate",
                    "Essential for all life",
                    "Can disrupt technology"
                ],
                "narration": "The Sun's influence on Earth is profound and far-reaching. It drives our planet's weather patterns through heating the atmosphere and oceans, creating wind currents and ocean circulation. The Sun's energy is absolutely essential for all life on Earth - plants use it for photosynthesis, which forms the base of the food chain. However, solar activity can also pose challenges to our technology. Solar storms can disrupt satellite communications, GPS systems, and even power grids. Understanding the Sun's behavior is crucial for protecting our technological infrastructure."
            },
            {
                "title": "Solar Research",
                "bullets": [
                    "Parker Solar Probe: Touching the Sun",
                    "Solar energy: Renewable power",
                    "Space weather: Protecting Earth"
                ],
                "narration": "Our understanding of the Sun continues to advance through cutting-edge research. The Parker Solar Probe, launched in 2018, is the first spacecraft to fly through the Sun's corona, collecting unprecedented data about solar wind and magnetic fields. Solar energy technology is rapidly advancing, with more efficient solar panels and energy storage systems being developed. Understanding space weather and the Sun's role in climate change is crucial for predicting Earth's future climate patterns and developing strategies to address global warming."
            }
        ]
    }
    
    try:
        # Initialize video generator
        video_generator = VideoGenerator()
        print("✅ Video generator initialized")
        
        # Save real content
        with open("real_sun_facts.json", 'w') as f:
            json.dump(real_sun_content, f, indent=2)
        print("💾 Real Sun facts saved")
        
        # Convert to script format
        script_lines = []
        for slide in real_sun_content.get('slides', []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get('bullets', []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video
        print("🎬 Generating Sun video with REAL facts...")
        output_path = "real_sun_facts_video.mp4"
        
        video_path = video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=8.0,
            width=1280,
            height=720,
            fps=30,
            topic="The Sun: Our Star"
        )
        
        print(f"✅ Real Sun facts video generated successfully!")
        print(f"📁 File: {video_path}")
        print(f"📏 Size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        print(f"⏱️ Duration: {len(real_sun_content.get('slides', [])) * 8} seconds")
        print(f"📊 Slides: {len(real_sun_content.get('slides', []))}")
        
        return video_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    video_path = create_real_sun_facts_video()
    
    if video_path:
        print(f"\n🎉 Real Sun facts video created successfully!")
        print(f"📹 Check '{video_path}' for your video with ACTUAL Sun facts!")
        print("🌞 This video contains real information about the Sun, not placeholder content!")
        print("📊 Facts included: Sun's mass, temperature, structure, solar activity, and impact on Earth")
    else:
        print(f"\n❌ Failed to create video") 