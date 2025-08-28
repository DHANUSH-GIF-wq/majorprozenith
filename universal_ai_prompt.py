#!/usr/bin/env python3
"""
Universal AI Prompt System for NotebookLM-Style Slide-to-Video Generation
Master prompt that handles any topic with multiple subtopic types and enhanced formatting
"""

import json
import logging
from typing import Dict, Any, List, Optional
from ai_service import AIService
from video_generator import VideoGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalAIPrompt:
    """
    Universal AI Prompt System for generating NotebookLM-style slide-to-video content
    Handles any topic with multiple subtopic types and enhanced formatting
    """
    
    def __init__(self):
        self.ai_service = AIService()
        self.video_generator = VideoGenerator()
        
        # Define different subtopic types for variety
        self.subtopic_types = {
            "definition": {
                "description": "Clear definitions and explanations",
                "layout": "clean minimal, concept fade-in",
                "style": "simple, direct language"
            },
            "comparison": {
                "description": "Compare and contrast different concepts",
                "layout": "side-by-side comparison, alternating reveals",
                "style": "balanced, objective analysis"
            },
            "process": {
                "description": "Step-by-step processes and workflows",
                "layout": "timeline style, sequential reveals",
                "style": "logical, sequential explanation"
            },
            "advantages_disadvantages": {
                "description": "Pros and cons analysis",
                "layout": "two-column grid, pros/cons reveal",
                "style": "balanced, analytical approach"
            },
            "case_study": {
                "description": "Real-world examples and applications",
                "layout": "storyboard style, narrative flow",
                "style": "engaging, practical examples"
            },
            "timeline": {
                "description": "Historical development and evolution",
                "layout": "horizontal timeline, chronological reveal",
                "style": "chronological, developmental focus"
            },
            "classification": {
                "description": "Categorization and classification systems",
                "layout": "hierarchical tree, category reveals",
                "style": "organized, systematic approach"
            },
            "principles": {
                "description": "Core principles and fundamental concepts",
                "layout": "card-based grid, principle highlights",
                "style": "foundational, principle-based"
            }
        }
    
    def generate_universal_prompt(self, topic: str, subtopics: List[str] = None, 
                                level: str = "beginner", num_slides: int = 8) -> str:
        """
        Generate the master universal AI prompt for NotebookLM-style content
        
        Args:
            topic: Main topic to cover
            subtopics: Optional list of specific subtopics to include
            level: Audience level (beginner, intermediate, advanced)
            num_slides: Number of slides to generate
            
        Returns:
            Complete AI prompt string
        """
        
        # Analyze topic for dynamic adaptation
        topic_category = self.ai_service._categorize_topic(topic)
        topic_complexity = self._analyze_topic_complexity(topic)
        
        # Determine optimal subtopic types based on topic
        recommended_types = self._get_recommended_subtopic_types(topic, topic_category)
        
        # Build the master prompt
        prompt = f"""
You are an AI system that generates video slideshows with synced narration in Google NotebookLM style.

## 🎯 TASK
Create a professional presentation for: "{topic}"
Audience Level: {level}
Target Slides: {num_slides}
Topic Category: {topic_category}
Complexity Level: {topic_complexity}

## 📋 CRITICAL STYLE RULES - NEVER VIOLATE
- NEVER use question marks (?) anywhere in any content
- NEVER start sentences with "What", "How", "Why", "When", "Where", "Which"
- Write ONLY clear, declarative statements
- Use simple, direct language appropriate for {level} level
- Focus on understanding, not memorization
- Make each slide build on the previous one
- Avoid jargon and complex terminology
- Write like explaining to a friend
- Ensure NO overlapping text on slides
- Use proper spacing and clean formatting

## 🎨 NOTEBOOKLM-STYLE REQUIREMENTS
- Create clean, minimal, focused slides
- Each slide should have clear subtopics and detailed content
- Include proper introduction, main content sections, and conclusion
- Use professional presentation formatting
- Focus on one main concept per slide
- Use concrete examples and real-world applications
- Ensure slides are visually balanced and non-cluttered

## 📊 CONTENT REQUIREMENTS
- Start with a clear title slide and agenda
- Break down the topic into logical subtopics
- Provide detailed explanations for each concept
- Include multiple examples and real-world applications
- Use professional language and clear structure
- End with a comprehensive summary and key takeaways

## 🎭 SUBTOPIC TYPE VARIETY
Use these different subtopic types to create engaging, non-repetitive content:

{self._format_subtopic_types(recommended_types)}

## 📝 SLIDE STRUCTURE REQUIREMENTS

Each slide must include:
- title: clean, focused slide title (max 6 words, no questions)
- subtopics: 2-3 main subtopics for this slide (max 5 words each)
- bullets: 3-6 concise bullet points (only keywords or short phrases, max 7 words each)
- narration: 80-120 words of flowing explanation that teaches the concept clearly
- examples: 1-2 concrete examples that illustrate the concepts clearly
- visual_prompts: 1-2 prompts describing clean, minimal visuals for this slide
- layout: suggested animation style based on subtopic type

## 🎬 SLIDE TYPES TO INCLUDE
1. Title Slide: Topic introduction with clean, minimal design
2. Overview: What will be covered (agenda-style)
3. Introduction: What the topic is and why it matters
4. Main Content Slides: Detailed explanations with varied subtopic types
5. Examples/Applications: Real-world usage and case studies
6. Summary: Key takeaways and next steps

## 🎯 CONTENT FOCUS
{focus_instruction}

## 📋 OUTPUT FORMAT
Return ONLY valid JSON with this exact structure:
{{
  "topic": "{topic}",
  "level": "{level}",
  "category": "{topic_category}",
  "complexity": "{topic_complexity}",
  "slides": [
    {{
      "title": "clean slide title",
      "subtopics": ["subtopic1", "subtopic2"],
      "bullets": ["bullet1", "bullet2", "bullet3"],
      "narration": "detailed explanation that expands on bullets with context and examples",
      "examples": ["example1", "example2"],
      "visual_prompts": ["visual description 1", "visual description 2"],
      "layout": "suggested animation style",
      "subtopic_type": "definition|comparison|process|advantages_disadvantages|case_study|timeline|classification|principles"
    }}
  ]
}}

IMPORTANT: 
- Do not include markdown fences or any text outside JSON
- Ensure all text is clean, professional, and free of question marks
- Make narration significantly more detailed than bullet points
- Vary subtopic types to avoid repetition
- Keep slides visually clean and non-overlapping
        """
        
        return prompt
    
    def _analyze_topic_complexity(self, topic: str) -> str:
        """Analyze topic complexity for appropriate content depth"""
        word_count = len(topic.split())
        if word_count <= 2:
            return "simple"
        elif word_count <= 4:
            return "moderate"
        else:
            return "complex"
    
    def _get_recommended_subtopic_types(self, topic: str, category: str) -> List[str]:
        """Get recommended subtopic types based on topic and category"""
        base_types = ["definition", "process", "case_study"]
        
        # Add category-specific types
        category_mappings = {
            "technology": ["comparison", "timeline", "principles"],
            "science": ["classification", "process", "principles"],
            "business": ["advantages_disadvantages", "case_study", "process"],
            "education": ["definition", "process", "case_study"],
            "health": ["process", "advantages_disadvantages", "case_study"],
            "arts": ["comparison", "timeline", "case_study"],
            "nature": ["classification", "process", "timeline"],
            "space": ["timeline", "principles", "case_study"]
        }
        
        additional_types = category_mappings.get(category, ["comparison", "timeline"])
        return base_types + additional_types[:2]  # Limit to 5 total types
    
    def _format_subtopic_types(self, types: List[str]) -> str:
        """Format subtopic types for the prompt"""
        formatted = []
        for t in types:
            if t in self.subtopic_types:
                info = self.subtopic_types[t]
                formatted.append(f"- {t}: {info['description']} ({info['layout']})")
        return "\n".join(formatted)
    
    def generate_structured_content(self, topic: str, subtopics: List[str] = None,
                                  level: str = "beginner", num_slides: int = 8,
                                  max_retries: int = 3) -> Dict[str, Any]:
        """
        Generate structured content using the universal prompt
        
        Args:
            topic: Main topic to cover
            subtopics: Optional list of specific subtopics
            level: Audience level
            num_slides: Number of slides
            max_retries: Maximum retry attempts
            
        Returns:
            Structured content dictionary
        """
        
        prompt = self.generate_universal_prompt(topic, subtopics, level, num_slides)
        
        for attempt in range(max_retries):
            try:
                response = self.ai_service.model.generate_content(
                    prompt,
                    generation_config=self.ai_service.model.generation_config(
                        temperature=0.7,
                        top_p=0.9,
                        top_k=50,
                        max_output_tokens=2048,
                    )
                )
                
                if response and hasattr(response, 'text'):
                    content = response.text.strip()
                    
                    # Clean the response
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    
                    # Parse JSON
                    structured_data = json.loads(content)
                    
                    # Validate structure
                    if self._validate_structure(structured_data):
                        logger.info(f"Structured content generated successfully (attempt {attempt + 1})")
                        return structured_data
                    else:
                        raise ValueError("Invalid structure in generated content")
                        
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
                
                import time
                time.sleep(0.5 * (attempt + 1))
        
        raise Exception("Failed to generate structured content after all retry attempts")
    
    def _validate_structure(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of generated content"""
        required_keys = ["topic", "level", "slides"]
        
        if not all(key in data for key in required_keys):
            return False
        
        if not isinstance(data["slides"], list):
            return False
        
        for slide in data["slides"]:
            required_slide_keys = ["title", "subtopics", "bullets", "narration"]
            if not all(key in slide for key in required_slide_keys):
                return False
        
        return True
    
    def generate_video_from_content(self, structured_data: Dict[str, Any], 
                                   output_path: str = None) -> str:
        """
        Generate video from structured content
        
        Args:
            structured_data: Structured content from generate_structured_content
            output_path: Output video path
            
        Returns:
            Path to generated video
        """
        
        if output_path is None:
            topic = structured_data.get("topic", "presentation")
            output_path = f"universal_{topic.lower().replace(' ', '_')}.mp4"
        
        # Convert structured data to script format
        script_lines = []
        for slide in structured_data.get("slides", []):
            script_lines.append(f"### {slide.get('title', 'Untitled')}")
            for bullet in slide.get("bullets", []):
                script_lines.append(f"- {bullet}")
            script_lines.append("")
        
        script = "\n".join(script_lines)
        
        # Generate video
        video_path = self.video_generator.generate_slideshow_video(
            script=script,
            output_path=output_path,
            seconds_per_slide=8.0,
            width=1280,
            height=720,
            fps=30,
            topic=structured_data.get("topic", "Presentation")
        )
        
        return video_path

def demo_universal_prompt():
    """Demo the universal AI prompt system"""
    
    print("🎬 Universal AI Prompt System Demo")
    print("=" * 50)
    
    # Initialize the system
    try:
        universal_prompt = UniversalAIPrompt()
        print("✅ Universal AI Prompt system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return False
    
    # Demo topics
    demo_topics = [
        "Machine Learning Basics",
        "Climate Change Science",
        "Digital Marketing Strategies"
    ]
    
    for topic in demo_topics:
        print(f"\n📚 Generating content for: {topic}")
        
        try:
            # Generate structured content
            structured_data = universal_prompt.generate_structured_content(
                topic=topic,
                level="beginner",
                num_slides=6,
                max_retries=2
            )
            
            print(f"✅ Content generated successfully")
            print(f"📊 Generated {len(structured_data.get('slides', []))} slides")
            print(f"🏷️ Topic category: {structured_data.get('category', 'N/A')}")
            print(f"📈 Complexity: {structured_data.get('complexity', 'N/A')}")
            
            # Show slide types used
            slide_types = [slide.get('subtopic_type', 'unknown') for slide in structured_data.get('slides', [])]
            print(f"🎭 Slide types used: {', '.join(set(slide_types))}")
            
            # Generate video
            print(f"🎥 Generating video...")
            video_path = universal_prompt.generate_video_from_content(structured_data)
            
            print(f"✅ Video generated: {video_path}")
            
        except Exception as e:
            print(f"❌ Error processing {topic}: {e}")
            continue
    
    print("\n🎉 Universal AI Prompt demo completed!")
    return True

if __name__ == "__main__":
    demo_universal_prompt() 