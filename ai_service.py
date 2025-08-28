import google.generativeai as genai
import logging
from typing import Optional, Dict, Any, List
import requests
from config import Config
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """Handles AI model interactions"""
    
    def __init__(self):
        self.config = Config()
        self._validate_and_configure()
        self.model = None
        self._initialize_model()
    
    def _validate_and_configure(self):
        """Validate configuration and setup Gemini API"""
        try:
            self.config.validate_config()
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise
    
    def _initialize_model(self):
        """Initialize the Gemini model"""
        try:
            self.model = genai.GenerativeModel("gemini-2.5-pro")
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def generate_response(self, prompt: str, max_retries: int = 2) -> str:
        """
        Generate natural, conversational response from AI model
        
        Args:
            prompt: User input prompt
            max_retries: Maximum number of retry attempts (reduced for speed)
            
        Returns:
            Natural AI response without structured formatting
        """
        for attempt in range(max_retries):
            try:
                if not self.model:
                    raise ValueError("Model not initialized")
                
                # Create a natural conversation prompt
                conversation_prompt = f"""
You are a helpful AI assistant. Provide a natural, conversational response to the user's message.
Keep your response friendly, informative, and easy to understand. Don't use any special formatting, 
bullet points, or structured layouts unless specifically asked for.

User message: {prompt}

Please respond naturally:
"""
                
                # Use faster generation settings for natural responses
                response = self.model.generate_content(
                    conversation_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.8,  # Slightly higher for more natural responses
                        top_p=0.9,
                        top_k=50,
                        max_output_tokens=1024,  # Shorter for faster responses
                    )
                )
                
                if response and hasattr(response, 'text'):
                    logger.info(f"AI response generated successfully (attempt {attempt + 1})")
                    return response.text.strip()
                else:
                    raise ValueError("Empty or invalid response from model")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
                
                # Very short wait time for instant retries
                import time
                time.sleep(0.2 * (attempt + 1))  # Even faster retries
        
        raise Exception("Failed to generate response after all retry attempts")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": "gemini-2.5-pro",
            "api_configured": bool(self.config.GEMINI_API_KEY),
            "model_initialized": bool(self.model)
        }
    
    def test_connection(self) -> bool:
        """Test if the AI service is working properly"""
        try:
            test_response = self.generate_response("Hello, this is a test message.")
            return bool(test_response and len(test_response) > 0)
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False 

    def generate_explainer(
        self,
        topic: str,
        level: str = "beginner",
        num_slides: int = 6,
        avoid_text: Optional[str] = None,
        max_retries: int = 3,
    ) -> str:
        """
        Generate a fresh explainer script for a topic (distinct from prior chat text).

        Args:
            topic: Subject to explain
            level: Audience level (e.g., beginner, intermediate, advanced)
            num_slides: Target number of sections/slides in the script
            avoid_text: Optional text to avoid repeating (e.g., last chat response)
            max_retries: Retry attempts

        Returns:
            Structured explainer script as plain text using slide headers and bullets.
        """
        constraints = f"Avoid repeating the following text and produce novel explanations: {avoid_text[:800]}" if avoid_text else ""
        prompt = f"""
You are a master teacher. Create an easy-to-understand explainer for the topic: "{topic}".
Audience level: {level}.
Structure the output as {num_slides} short slides with clear headers and 3-5 concise bullet points each.
Use analogies, simple language, and step-by-step logic. Keep it self-contained and different from any prior text.
{constraints}

Formatting rules:
- Start each slide with: "### Slide X: <Title>"
- Then 3-5 bullets beginning with "- ". Keep bullets short.
- End with a brief recap slide.
Do NOT include code fences or markdown outside the specified format.
        """

        for attempt in range(max_retries):
            try:
                if not self.model:
                    raise ValueError("Model not initialized")
                response = self.model.generate_content(prompt)
                # Try common fields for Gemini SDKs
                text = getattr(response, "text", None)
                if not text and hasattr(response, "candidates"):
                    try:
                        candidates = response.candidates or []
                        for c in candidates:
                            parts = getattr(getattr(c, "content", None), "parts", None)
                            if parts:
                                joined = "\n".join([getattr(p, "text", "") for p in parts if getattr(p, "text", "")])
                                if joined.strip():
                                    text = joined
                                    break
                    except Exception:
                        pass
                if not text:
                    raise ValueError("Empty response from model")
                return text.strip()
            except Exception as e:
                logger.warning(f"Explainer generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("Explainer generation failed after all retries")
                    # Fallback minimal slide deck so the pipeline can continue
                    fallback = [
                        "### Slide 1: Introduction",
                        f"- What is {topic}?",
                        "- Why it matters",
                        "- Real-world intuition",
                        "### Slide 2: Core Ideas",
                        "- Key concept 1",
                        "- Key concept 2",
                        "- Simple analogy",
                        "### Slide 3: How it works",
                        "- Step 1",
                        "- Step 2",
                        "- Step 3",
                        "### Slide 4: Common Pitfalls",
                        "- Misconception 1",
                        "- Misconception 2",
                        "### Slide 5: Recap",
                        "- Summarize big ideas",
                        "- Next steps",
                    ]
                    return "\n".join(fallback)

    def generate_explainer_structured(
        self,
        topic: str,
        level: str = "beginner",
        num_slides: int = 8,
        avoid_text: Optional[str] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate a high-quality explainer with structured slides in Google NotebookLM style:
        [{ title, subtopics[], bullets[], narration, examples[], visual_prompts[] }]
        """
        constraints = (
            f"Avoid repeating the following text and produce novel explanations: {avoid_text[:800]}"
            if avoid_text else ""
        )
        
        # Analyze topic for dynamic content adaptation
        topic_words = len(topic.split())
        topic_category = self._categorize_topic(topic)
        
        if topic_words <= 3:
            # Simple topic - focused presentation
            num_slides = min(6, num_slides)
            focus_instruction = f"Create a clear, step-by-step explanation of {topic} with practical examples and real-world applications."
        elif topic_words <= 6:
            # Medium topic - comprehensive coverage
            num_slides = min(8, num_slides)
            focus_instruction = f"Provide comprehensive coverage of {topic} with clear subtopics, detailed explanations, and multiple examples."
        else:
            # Complex topic - thorough breakdown
            num_slides = min(10, num_slides)
            focus_instruction = f"Break down {topic} into logical sections with detailed explanations and comprehensive examples."
        
        prompt = f"""
You are an AI system that generates video slideshows with synced narration in Google NotebookLM style.

## 🎯 TASK
Create a professional VIDEO presentation for: "{topic}"
Audience Level: {level}
Target Slides: {num_slides}
Video Duration: ~{num_slides * 8} seconds (8 seconds per slide)

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

## 🎨 VIDEO-OPTIMIZED REQUIREMENTS
- Create clean, minimal, focused slides optimized for video viewing
- Each slide should have clear subtopics and detailed content
- Include proper introduction, main content sections, and conclusion
- Use professional presentation formatting suitable for video
- Focus on one main concept per slide (8 seconds of content)
- Use concrete examples and real-world applications
- Ensure slides are visually balanced and non-cluttered for video display
- Design for smooth transitions between slides
- Optimize text size and spacing for video viewing

## 📊 CONTENT REQUIREMENTS
- {focus_instruction}
- Start with a clear title slide and agenda
- Break down the topic into logical subtopics
- Provide detailed explanations for each concept
- Include multiple examples and real-world applications
- Use professional language and clear structure
- End with a comprehensive summary and key takeaways

## 🎭 VIDEO SUBTOPIC TYPES
Use these different subtopic types to create engaging, non-repetitive video content:

- definition: Clear definitions and explanations (clean minimal, concept fade-in, 8 seconds)
- comparison: Compare and contrast different concepts (side-by-side comparison, alternating reveals, 8 seconds)
- process: Step-by-step processes and workflows (timeline style, sequential reveals, 8 seconds)
- advantages_disadvantages: Pros and cons analysis (two-column grid, pros/cons reveal, 8 seconds)
- case_study: Real-world examples and applications (storyboard style, narrative flow, 8 seconds)
- timeline: Historical development and evolution (horizontal timeline, chronological reveal, 8 seconds)
- classification: Categorization and classification systems (hierarchical tree, category reveals, 8 seconds)
- principles: Core principles and fundamental concepts (card-based grid, principle highlights, 8 seconds)

## 📝 SLIDE STRUCTURE REQUIREMENTS

Each slide must include:
- title: clean, focused slide title (max 6 words, no questions)
- subtopics: 2-3 main subtopics for this slide (max 5 words each)
- bullets: 3-6 concise bullet points (only keywords or short phrases, max 7 words each)
- narration: 80-120 words of flowing explanation that teaches the concept clearly (timed for ~8 seconds)
- examples: 1-2 concrete examples that illustrate the concepts clearly
- visual_prompts: 1-2 prompts describing clean, minimal visuals for this slide
- layout: suggested animation style based on subtopic type
- subtopic_type: one of the 8 types listed above
- timing: 8 seconds per slide for smooth video flow

## 🎬 VIDEO SLIDE TYPES TO INCLUDE
1. Title Slide: Topic introduction with clean, minimal design (8 seconds)
2. Overview: What will be covered (agenda-style, 8 seconds)
3. Introduction: What the topic is and why it matters (8 seconds)
4. Main Content Slides: Detailed explanations with varied subtopic types (8 seconds each)
5. Examples/Applications: Real-world usage and case studies (8 seconds)
6. Summary: Key takeaways and next steps (8 seconds)

{constraints}

## 📋 OUTPUT FORMAT
Return ONLY valid JSON with this exact structure:
{{
  "topic": "{topic}",
  "level": "{level}",
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
- Optimize content for video viewing and narration timing
- Ensure smooth flow between slides for video presentation
        """

        for attempt in range(max_retries):
            try:
                if not self.model:
                    raise ValueError("Model not initialized")
                response = self.model.generate_content(prompt)
                text = getattr(response, "text", None)
                if not text and hasattr(response, "candidates"):
                    try:
                        candidates = response.candidates or []
                        for c in candidates:
                            parts = getattr(getattr(c, "content", None), "parts", None)
                            if parts:
                                joined = "\n".join([getattr(p, "text", "") for p in parts if getattr(p, "text", "")])
                                if joined.strip():
                                    text = joined
                                    break
                    except Exception:
                        pass
                if not text:
                    raise ValueError("Empty response from model")
                import json as _json
                data = _json.loads(text)
                # Basic validation
                if not isinstance(data, dict) or "slides" not in data:
                    raise ValueError("Invalid JSON structure")
                
                # Clean the content to remove any question marks
                data = self._clean_content_data(data)
                
                return data
            except Exception as e:
                logger.warning(f"Structured explainer attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("Structured explainer failed after all retries; attempting knowledge-backed fallback")
                    kb = self.fetch_topic_knowledge(topic)
                    if kb and kb.get("summary"):
                        return self._build_structured_from_knowledge(topic, level, num_slides, kb)
                    # ultimate fallback
                    return self._build_placeholder_structured(topic, level)
    
    def _clean_content_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean content data to remove question marks and improve quality"""
        if "slides" in data:
            for slide in data["slides"]:
                # Clean title
                if "title" in slide:
                    slide["title"] = self._clean_text(slide["title"])
                
                # Clean subtopics
                if "subtopics" in slide:
                    slide["subtopics"] = [self._clean_text(subtopic) for subtopic in slide["subtopics"]]
                
                # Clean bullets
                if "bullets" in slide:
                    slide["bullets"] = [self._clean_text(bullet) for bullet in slide["bullets"]]
                
                # Clean narration
                if "narration" in slide:
                    slide["narration"] = self._clean_text(slide["narration"])
                
                # Clean examples
                if "examples" in slide:
                    slide["examples"] = [self._clean_text(example) for example in slide["examples"]]
        
        return data
    
    def _clean_text(self, text: str) -> str:
        """Clean text to remove question marks and improve clarity"""
        if not text:
            return text
        
        # Remove question marks and convert to statements
        text = text.replace("?", ".")
        text = text.replace("??", ".")
        text = text.replace("???", ".")
        text = text.replace("????", ".")
        text = text.replace("?????", ".")
        
        # Remove any remaining question marks
        text = text.replace("?", "")
        
        # Convert questions to statements - MORE AGGRESSIVE
        question_starters = [
            "What is", "How does", "Why do", "When do", "Where do", "Which is",
            "What are", "How are", "Why are", "When are", "Where are", "Which are",
            "What", "How", "Why", "When", "Where", "Which"
        ]
        
        # Split into sentences and process each
        sentences = text.split('.')
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if sentence starts with a question starter
            for starter in question_starters:
                if sentence.lower().startswith(starter.lower()):
                    # Convert question to statement
                    if starter.lower() == "what is":
                        sentence = sentence.replace(starter, "This is", 1)
                    elif starter.lower() == "how does":
                        sentence = sentence.replace(starter, "This works by", 1)
                    elif starter.lower() == "why do":
                        sentence = sentence.replace(starter, "This happens because", 1)
                    elif starter.lower() == "when do":
                        sentence = sentence.replace(starter, "This occurs when", 1)
                    elif starter.lower() == "where do":
                        sentence = sentence.replace(starter, "This happens in", 1)
                    elif starter.lower() == "which is":
                        sentence = sentence.replace(starter, "This is", 1)
                    elif starter.lower() == "what are":
                        sentence = sentence.replace(starter, "These are", 1)
                    elif starter.lower() == "how are":
                        sentence = sentence.replace(starter, "These work by", 1)
                    elif starter.lower() == "why are":
                        sentence = sentence.replace(starter, "These exist because", 1)
                    elif starter.lower() == "when are":
                        sentence = sentence.replace(starter, "These occur when", 1)
                    elif starter.lower() == "where are":
                        sentence = sentence.replace(starter, "These exist in", 1)
                    elif starter.lower() == "which are":
                        sentence = sentence.replace(starter, "These are", 1)
                    elif starter.lower() == "what":
                        sentence = sentence.replace(starter, "This", 1)
                    elif starter.lower() == "how":
                        sentence = sentence.replace(starter, "This works by", 1)
                    elif starter.lower() == "why":
                        sentence = sentence.replace(starter, "This happens because", 1)
                    elif starter.lower() == "when":
                        sentence = sentence.replace(starter, "This occurs when", 1)
                    elif starter.lower() == "where":
                        sentence = sentence.replace(starter, "This happens in", 1)
                    elif starter.lower() == "which":
                        sentence = sentence.replace(starter, "This", 1)
                    break
            
            cleaned_sentences.append(sentence)
        
        # Join sentences back together
        text = ". ".join(cleaned_sentences)
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', ':')):
            text = text + '.'
        
        return text

    def generate_explainer_structured_free(
        self,
        topic: str,
        level: str = "beginner",
        num_slides: int = 6,
        avoid_text: Optional[str] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate structured content using free alternatives (no API key required)
        """
        try:
            # Try OpenAI API first (if available)
            if self._try_openai_generation(topic, level, num_slides, avoid_text):
                return self._try_openai_generation(topic, level, num_slides, avoid_text)
            
            # Fallback to local template-based generation
            return self._generate_local_content(topic, level, num_slides)
            
        except Exception as e:
            logger.error(f"Free content generation failed: {e}")
            # Ultimate fallback
            return self._build_placeholder_structured(topic, level)
    
    def _try_openai_generation(self, topic: str, level: str, num_slides: int, avoid_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Try OpenAI API for content generation (free tier available)"""
        try:
            import openai
            
            # Check if OpenAI API key is available
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return None
            
            openai.api_key = api_key
            
            prompt = f"""
You are an AI system that generates video slideshows with synced narration in Google NotebookLM style.

## 🎯 TASK
Create a professional VIDEO presentation for: "{topic}"
Audience Level: {level}
Target Slides: {num_slides}
Video Duration: ~{num_slides * 8} seconds (8 seconds per slide)

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

## 🎨 VIDEO-OPTIMIZED REQUIREMENTS
- Create clean, minimal, focused slides optimized for video viewing
- Each slide should have clear subtopics and detailed content
- Include proper introduction, main content sections, and conclusion
- Use professional presentation formatting suitable for video
- Focus on one main concept per slide (8 seconds of content)
- Use concrete examples and real-world applications
- Ensure slides are visually balanced and non-cluttered for video display
- Design for smooth transitions between slides
- Optimize text size and spacing for video viewing

## 📊 CONTENT REQUIREMENTS
- Start with a clear title slide and agenda
- Break down the topic into logical subtopics
- Provide detailed explanations for each concept
- Include multiple examples and real-world applications
- Use professional language and clear structure
- End with a comprehensive summary and key takeaways

## 🎭 VIDEO SUBTOPIC TYPES
Use these different subtopic types to create engaging, non-repetitive video content:

- definition: Clear definitions and explanations (clean minimal, concept fade-in, 8 seconds)
- comparison: Compare and contrast different concepts (side-by-side comparison, alternating reveals, 8 seconds)
- process: Step-by-step processes and workflows (timeline style, sequential reveals, 8 seconds)
- advantages_disadvantages: Pros and cons analysis (two-column grid, pros/cons reveal, 8 seconds)
- case_study: Real-world examples and applications (storyboard style, narrative flow, 8 seconds)
- timeline: Historical development and evolution (horizontal timeline, chronological reveal, 8 seconds)
- classification: Categorization and classification systems (hierarchical tree, category reveals, 8 seconds)
- principles: Core principles and fundamental concepts (card-based grid, principle highlights, 8 seconds)

## 📝 SLIDE STRUCTURE REQUIREMENTS

Each slide must include:
- title: clean, focused slide title (max 6 words, no questions)
- subtopics: 2-3 main subtopics for this slide (max 5 words each)
- bullets: 3-6 concise bullet points (only keywords or short phrases, max 7 words each)
- narration: 80-120 words of flowing explanation that teaches the concept clearly (timed for ~8 seconds)
- examples: 1-2 concrete examples that illustrate the concepts clearly
- visual_prompts: 1-2 prompts describing clean, minimal visuals for this slide
- layout: suggested animation style based on subtopic type
- subtopic_type: one of the 8 types listed above
- timing: 8 seconds per slide for smooth video flow

## 🎬 VIDEO SLIDE TYPES TO INCLUDE
1. Title Slide: Topic introduction with clean, minimal design (8 seconds)
2. Overview: What will be covered (agenda-style, 8 seconds)
3. Introduction: What the topic is and why it matters (8 seconds)
4. Main Content Slides: Detailed explanations with varied subtopic types (8 seconds each)
5. Examples/Applications: Real-world usage and case studies (8 seconds)
6. Summary: Key takeaways and next steps (8 seconds)

## 📋 OUTPUT FORMAT
Return ONLY valid JSON with this exact structure:
{{
  "topic": "{topic}",
  "level": "{level}",
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
- Optimize content for video viewing and narration timing
- Ensure smooth flow between slides for video presentation
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a master educator creating professional presentations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            import json
            data = json.loads(content)
            
            # Clean the content
            data = self._clean_content_data(data)
            return data
            
        except Exception as e:
            logger.warning(f"OpenAI generation failed: {e}")
            return None
    
    def _generate_local_content(self, topic: str, level: str, num_slides: int) -> Dict[str, Any]:
        """Generate content using local templates (no API required)"""
        
        # Template-based content generation with detailed subtopic explanations
        templates = {
            'technology': {
                'slides': [
                    {
                        'title': f'Introduction to {topic}',
                        'subtopics': ['Core Concepts', 'Key Components', 'Applications'],
                        'bullets': [
                            f'{topic} represents modern technological advancement',
                            'It combines multiple technical disciplines',
                            'Used across various industries and applications',
                            'Continuously evolving with new developments'
                        ],
                        'narration': f'Let me explain the core concepts of {topic} in detail. The core concepts form the fundamental foundation that makes this technology work. These concepts include understanding the basic principles, algorithms, and methodologies that drive the entire system. The core concepts are essential because they guide all decision-making processes and implementation strategies. Understanding these core concepts is crucial for anyone working with this technology, as they provide the theoretical framework that supports all practical applications. These concepts have been developed through years of research and experimentation, and they continue to evolve as new discoveries are made. Next, let me explain the key components in detail. The key components are the essential building blocks that make this technology functional and effective. Each component has a specific role and responsibility within the overall system architecture. These components work together in harmony to create a complete and robust solution. Understanding each component individually helps us appreciate how they contribute to the overall functionality. The components are designed to be modular, allowing for easy maintenance, updates, and scalability. Finally, let me explain the applications in detail. The applications of {topic} are vast and diverse, spanning multiple industries from healthcare to finance, from education to entertainment. This technology is used to solve complex problems that were previously impossible to address. The applications demonstrate the practical value and real-world impact of this technology. Each application showcases different aspects of the technology\'s capabilities and potential.',
                        'examples': [f'Companies use {topic} for automation', f'{topic} powers modern applications'],
                        'visual_prompts': ['Clean technology diagram', 'Modern interface design']
                    },
                    {
                        'title': 'Core Principles',
                        'subtopics': ['Fundamentals', 'Best Practices', 'Implementation'],
                        'bullets': [
                            'Understanding the basic principles is essential',
                            'Follow established best practices for success',
                            'Proper implementation ensures optimal results',
                            'Regular updates maintain system efficiency'
                        ],
                        'narration': f'Now let me explain the fundamentals of {topic} in detail. The fundamentals are the basic principles that everyone working with this technology must thoroughly understand. These principles guide all decision-making processes and provide the framework for successful implementation. Understanding these fundamentals is crucial because they form the foundation upon which all advanced concepts are built. The fundamentals include theoretical knowledge, practical skills, and conceptual understanding that enable effective problem-solving. These principles have been developed through extensive research and real-world testing, ensuring their reliability and effectiveness. Next, let me explain the best practices in detail. Best practices have been developed through years of experience, research, and continuous improvement. These practices ensure that implementations are successful, efficient, and maintainable. Following these best practices reduces errors, improves performance, and enhances user experience. These practices are based on lessons learned from successful projects and common pitfalls to avoid. They provide guidelines for optimal configuration, deployment, and maintenance strategies. Finally, let me explain implementation in detail. Implementation involves putting the principles and best practices into action through careful planning and execution. This requires understanding the specific requirements, constraints, and objectives of each project. Proper implementation ensures that the technology delivers the expected benefits and performs reliably under various conditions. Implementation includes system design, development, testing, deployment, and ongoing maintenance to ensure long-term success.',
                        'examples': ['Industry standards guide development', 'Successful projects follow proven methods'],
                        'visual_prompts': ['Principle flowchart', 'Best practice checklist']
                    },
                    {
                        'title': 'Real-World Applications',
                        'subtopics': ['Industry Use', 'Case Studies', 'Future Trends'],
                        'bullets': [
                            'Widely adopted across multiple industries',
                            'Proven success in various applications',
                            'Continuous innovation drives new uses',
                            'Future applications show great promise'
                        ],
                        'narration': f'Let me explain the industry use of {topic} in detail. This technology has been widely adopted across multiple industries, demonstrating its versatility, effectiveness, and practical value. Each industry has found unique ways to apply this technology to solve their specific challenges and improve their operations. The adoption rate continues to grow as more organizations recognize the significant benefits and competitive advantages this technology provides. Different industries have different requirements and constraints, and this technology has proven adaptable to meet these diverse needs. The widespread adoption across industries validates the technology\'s effectiveness and reliability. Next, let me explain case studies in detail. Case studies provide real-world examples of successful implementations and demonstrate the practical value of this technology. These examples offer valuable insights into what works well and what challenges might arise during implementation. Case studies serve as learning opportunities for future projects and help organizations understand the potential benefits and risks. They showcase different approaches, methodologies, and outcomes that can inform decision-making processes. Finally, let me explain future trends in detail. The future of {topic} looks extremely promising with continuous innovation driving new applications and capabilities. Emerging trends suggest even more exciting developments ahead, with potential applications we haven\'t even imagined yet. The technology is evolving rapidly, with new features, capabilities, and use cases being discovered regularly. Future trends indicate increased integration, automation, and intelligence that will further enhance the technology\'s value and impact.',
                        'examples': ['Healthcare applications improve patient care', 'Financial systems enhance security'],
                        'visual_prompts': ['Industry application map', 'Success metrics chart']
                    }
                ]
            },
            'science': {
                'slides': [
                    {
                        'title': f'Understanding {topic}',
                        'subtopics': ['Scientific Basis', 'Key Theories', 'Research Methods'],
                        'bullets': [
                            f'{topic} is based on solid scientific principles',
                            'Research methods ensure accurate results',
                            'Theoretical frameworks guide understanding',
                            'Empirical evidence supports conclusions'
                        ],
                        'narration': f'Let me explain the scientific basis of {topic} in detail. The scientific basis provides the fundamental foundation for understanding this complex field and its various phenomena. It involves understanding the fundamental laws, principles, and mechanisms that govern this area of study. This scientific basis has been developed through rigorous research, experimentation, and validation processes. Understanding the scientific basis is crucial because it provides the theoretical framework that supports all practical applications and research endeavors. The scientific basis includes fundamental concepts, mathematical models, and theoretical frameworks that explain how and why things work. Next, let me explain the key theories in detail. Key theories in this field provide comprehensive frameworks for understanding complex phenomena and making predictions about future observations. These theories have been extensively tested, validated, and refined through years of research and experimentation. They help us understand relationships between different factors and provide explanations for observed phenomena. These theories serve as the foundation for further research and practical applications. Finally, let me explain research methods in detail. Research methods in this field ensure that conclusions are based on reliable, reproducible evidence and follow rigorous scientific standards. These methods include both experimental and observational approaches, each with their own strengths, limitations, and applications. Understanding these methods is essential for conducting valid research and interpreting results accurately. These methods have been developed and refined over decades of scientific practice.',
                        'examples': ['Laboratory experiments validate theories', 'Peer-reviewed studies confirm findings'],
                        'visual_prompts': ['Scientific diagram', 'Research methodology flowchart']
                    },
                    {
                        'title': 'Key Discoveries',
                        'subtopics': ['Historical Development', 'Major Breakthroughs', 'Current Research'],
                        'bullets': [
                            'Historical discoveries shaped current understanding',
                            'Major breakthroughs advanced the field significantly',
                            'Current research continues to expand knowledge',
                            'Future discoveries promise new insights'
                        ],
                        'narration': f'Let me explain the historical development of {topic} in detail. The historical development of this field shows how our understanding has evolved over time through the contributions of many researchers and scientists. Early discoveries laid the groundwork for current knowledge, while each generation of researchers built upon previous work to advance the field further. This historical context helps us understand why current theories, methods, and applications exist in their present form. The historical development reveals the challenges, controversies, and breakthroughs that shaped the field\'s evolution. Next, let me explain major breakthroughs in detail. Major breakthroughs in this field have significantly advanced our understanding and opened new areas of research and application. These breakthroughs often came from unexpected directions and required innovative thinking, creative approaches, and persistent effort. They have had lasting impacts on the field and continue to influence current research directions and practical applications. These breakthroughs represent paradigm shifts that fundamentally changed how we understand and approach problems in this field. Finally, let me explain current research in detail. Current research in this field continues to expand our knowledge and push the boundaries of understanding in exciting new directions. Researchers are exploring new questions, developing new methods, and discovering new applications that were previously unimaginable. This ongoing research ensures that the field remains dynamic, relevant, and continues to provide valuable insights and solutions.',
                        'examples': ['Nobel Prize-winning research', 'Recent breakthrough publications'],
                        'visual_prompts': ['Timeline of discoveries', 'Research impact diagram']
                    },
                    {
                        'title': 'Practical Applications',
                        'subtopics': ['Laboratory Use', 'Industrial Applications', 'Everyday Impact'],
                        'bullets': [
                            'Laboratory applications demonstrate principles',
                            'Industrial uses show practical value',
                            'Everyday applications affect daily life',
                            'Future applications hold great promise'
                        ],
                        'narration': f'Let me explain the laboratory use of {topic} in detail. Laboratory applications help researchers understand fundamental principles, test theoretical predictions, and develop new methodologies and techniques. These controlled experiments provide valuable insights that cannot be obtained through observation alone and allow for precise manipulation of variables. Laboratory work is essential for advancing our understanding and developing new applications. These laboratory applications serve as the foundation for larger-scale implementations and real-world applications. Next, let me explain industrial applications in detail. Industrial applications of this field show its practical value in solving real-world problems and improving industrial processes. These applications often involve scaling up laboratory findings to industrial processes and adapting theoretical knowledge to practical constraints. They demonstrate how scientific knowledge can be translated into practical benefits and economic value. Finally, let me explain everyday impact in detail. The everyday impact of this field affects our daily lives in numerous ways, often without us realizing it. From the technology we use to the products we consume, this field influences many aspects of modern life and society. Understanding this everyday impact helps us appreciate the importance and relevance of this field.',
                        'examples': ['Medical diagnostic tools', 'Environmental monitoring systems'],
                        'visual_prompts': ['Application diagram', 'Impact assessment chart']
                    }
                ]
            }
        }
        
        # Determine template based on topic
        topic_category = self._categorize_topic(topic)
        template = templates.get(topic_category, templates['technology'])
        
        # Customize template for specific topic
        slides = []
        for slide in template['slides']:
            customized_slide = slide.copy()
            customized_slide['title'] = slide['title'].replace('{topic}', topic)
            customized_slide['narration'] = slide['narration'].replace('{topic}', topic)
            slides.append(customized_slide)
        
        return {
            'topic': topic,
            'level': level,
            'slides': slides[:num_slides]
        }

    def fetch_topic_knowledge(self, topic: str) -> Dict[str, Any]:
        """Fetch summary, sections, and image candidates from Wikipedia/Wikimedia."""
        try:
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(topic)}"
            r = requests.get(summary_url, timeout=10)
            data = r.json() if r.status_code == 200 else {}
            images: List[str] = []
            # Try page media-list for richer images
            title = data.get("title", topic)
            media_url = f"https://en.wikipedia.org/api/rest_v1/page/media-list/{requests.utils.quote(title)}"
            rm = requests.get(media_url, timeout=10)
            if rm.status_code == 200:
                mdata = rm.json()
                for item in mdata.get("items", []):
                    srcset = item.get("srcset") or []
                    if srcset:
                        images.append(srcset[-1].get("src"))
                    elif item.get("original") and item["original"].get("source"):
                        images.append(item["original"]["source"])
            # sections via mobile-sections (best-effort)
            sections: List[Dict[str, Any]] = []
            try:
                sec_url = f"https://en.wikipedia.org/api/rest_v1/page/mobile-sections/{requests.utils.quote(title)}"
                rs = requests.get(sec_url, timeout=10)
                if rs.status_code == 200:
                    sdata = rs.json()
                    for s in (sdata.get("remaining", []) or []):
                        sec_title = s.get("line") or ""
                        sec_text = s.get("text") or ""
                        # strip html tags naive
                        import re as _re
                        sec_plain = _re.sub('<[^<]+?>', '', sec_text)
                        if sec_title and sec_plain:
                            sections.append({"title": sec_title, "text": sec_plain})
            except Exception:
                pass
            return {
                "summary": data.get("extract") or "",
                "description": data.get("description") or "",
                "title": title,
                "images": images[:10],
                "sections": sections[:12]
            }
        except Exception as e:
            logger.warning(f"Failed to fetch topic knowledge: {e}")
            return {}

    def _build_structured_from_knowledge(self, topic: str, level: str, num_slides: int, kb: Dict[str, Any]) -> Dict[str, Any]:
        summary = (kb.get("summary") or "").strip()
        sentences = [s.strip() for s in summary.replace("\n", " ").split('.') if s.strip()]
        # Prefer sections when available to ensure non-repetitive coverage
        sec_list = kb.get("sections") or []
        slides = []
        if sec_list:
            for i, sec in enumerate(sec_list[:num_slides]):
                sec_title = sec.get("title") or f"Section {i+1}"
                sec_text = sec.get("text") or ""
                # build bullets from sentences
                sbul = [t.strip() for t in sec_text.split('.') if t.strip()][:4]
                narration = ' '.join([t for t in sec_text.split('.') if t.strip()])
                slides.append({
                    "title": sec_title,
                    "bullets": sbul,
                    "narration": narration[:900],
                    "examples": [],
                    "visual_prompts": [f"Diagram: {sec_title}"]
                })
            # if not enough slides, pad from summary sentences
            if len(slides) < num_slides and sentences:
                remain = num_slides - len(slides)
                chunk = sentences[: remain * 3]
                for j in range(remain):
                    part = chunk[j*3:(j+1)*3]
                    if not part:
                        break
                    slides.append({
                        "title": f"{topic}: Key idea {len(slides)+1}",
                        "bullets": part[:3],
                        "narration": ' '.join(part)[:900],
                        "examples": [],
                        "visual_prompts": [f"Diagram related to {topic}"]
                    })
        else:
            # fallback: chunk summary
            per = max(2, max(1, len(sentences)) // max(3, num_slides))
            idx = 0
            for i in range(num_slides):
                chunk = sentences[idx: idx + per] or sentences[idx: idx + 2]
                idx += per
                if not chunk:
                    break
                title = f"{topic}: Key idea {i+1}" if i > 0 else f"What is {topic}?"
                bullets = chunk[:4]
                narration = " ".join(chunk)
                slides.append({
                    "title": title,
                    "bullets": bullets,
                    "narration": narration[:900],
                    "examples": [],
                    "visual_prompts": [f"Diagram related to {topic}"]
                })
        if not slides:
            slides = [{
                "title": f"About {topic}",
                "bullets": [summary[:90]],
                "narration": summary[:800],
                "examples": [],
                "visual_prompts": [f"Topic illustration: {topic}"]
            }]
        return {"topic": topic, "level": level, "slides": slides[:num_slides]}

    def _build_placeholder_structured(self, topic: str, level: str) -> Dict[str, Any]:
        slides = []
        slides.append({
            "title": f"What is {topic}?",
            "bullets": [f"Plain-language definition of {topic}", "Where it's used", "Analogy"],
            "narration": f"{topic} explained simply with an analogy and why it matters.",
            "examples": [f"Everyday example of {topic}"],
            "visual_prompts": [f"Simple diagram of {topic}"]
        })
        slides.append({
            "title": "Core ideas",
            "bullets": ["Idea 1", "Idea 2", "Idea 3"],
            "narration": "Key concepts step by step.",
            "examples": ["Before/after"],
            "visual_prompts": ["Step diagram"]
        })
        slides.append({
            "title": "Recap",
            "bullets": ["Definition", "Core ideas", "Takeaway"],
            "narration": "Wrap up.",
            "examples": ["Teach a friend"],
            "visual_prompts": ["Summary card"]
        })
        return {"topic": topic, "level": level, "slides": slides}

    def refine_structured_explainer(self, data: Dict[str, Any], topic: str, level: str = "beginner") -> Dict[str, Any]:
        """Post-process a structured explainer to ensure concrete, useful content.

        Rewrites placeholders and expands short narration using separate targeted prompts.
        """
        import copy
        refined = copy.deepcopy(data) if isinstance(data, dict) else {"topic": topic, "level": level, "slides": []}
        slides = refined.get("slides", [])

        def _gen(prompt: str) -> str:
            try:
                txt = self.generate_response(prompt)
                return txt.strip()
            except Exception:
                return ""

        for idx, slide in enumerate(slides):
            title = slide.get("title") or f"Slide {idx+1}"
            # Bullets
            bullets = slide.get("bullets") or []
            generic_tokens = {"idea 1", "idea 2", "idea 3", "definition", "core ideas", "one-liner takeaway", "setup", "steps", "result", "pitfall 1", "pitfall 2"}
            needs_bullets = (not bullets) or any(b.lower() in generic_tokens for b in bullets)
            if needs_bullets:
                btext = _gen(
                    f"Provide 4 concise, factual bullet points for a slide titled '{title}' explaining '{topic}' to a {level}. "
                    f"Avoid jargon; each bullet under 16 words. Return bullets separated by newline only."
                )
                new_bullets = [line.strip("- • \t ") for line in btext.splitlines() if line.strip()]
                if new_bullets:
                    slide["bullets"] = new_bullets[:5]
            # Narration
            narration = slide.get("narration") or ""
            if len(narration) < 80:
                ntext = _gen(
                    f"Write a 100-130 word friendly narration for slide '{title}' on '{topic}' for a {level}. "
                    f"Use a simple analogy and a concrete mini-example. Avoid fluff."
                )
                if len(ntext) > 60:
                    slide["narration"] = ntext
            # Examples
            examples = slide.get("examples") or []
            if not examples or any(e.lower().startswith("example") for e in examples):
                etext = _gen(
                    f"Give 2 concrete, everyday examples that illustrate '{title}' about '{topic}'. "
                    f"Each example under 20 words. Return as two lines."
                )
                ex = [line.strip("- • \t ") for line in etext.splitlines() if line.strip()]
                if ex:
                    slide["examples"] = ex[:2]
            # Visual prompts
            visual_prompts = slide.get("visual_prompts") or []
            if not visual_prompts:
                vp = _gen(
                    f"Suggest 2 short visual prompts (diagram/photo) to visualize '{title}' for '{topic}'. "
                    f"Each under 12 words. Return as two lines."
                )
                vps = [line.strip("- • \t ") for line in vp.splitlines() if line.strip()]
                if vps:
                    slide["visual_prompts"] = vps[:2]

        refined["slides"] = slides
        return refined

    def _categorize_topic(self, topic: str) -> str:
        """Categorize topic for dynamic content adaptation"""
        topic_lower = topic.lower()
        
        # Technology & Science
        if any(word in topic_lower for word in ['ai', 'machine learning', 'neural', 'algorithm', 'programming', 'software', 'computer', 'data', 'technology']):
            return 'technology'
        elif any(word in topic_lower for word in ['physics', 'chemistry', 'biology', 'science', 'research', 'experiment', 'molecular', 'atomic']):
            return 'science'
        # Business & Economics
        elif any(word in topic_lower for word in ['business', 'economics', 'finance', 'marketing', 'management', 'strategy', 'market', 'investment']):
            return 'business'
        # Education & Learning
        elif any(word in topic_lower for word in ['education', 'learning', 'teaching', 'study', 'academic', 'university', 'school', 'course']):
            return 'education'
        # Health & Medicine
        elif any(word in topic_lower for word in ['health', 'medical', 'medicine', 'disease', 'treatment', 'therapy', 'patient', 'clinical']):
            return 'health'
        # Arts & Culture
        elif any(word in topic_lower for word in ['art', 'music', 'culture', 'history', 'literature', 'design', 'creative', 'artist']):
            return 'arts'
        # Nature & Environment
        elif any(word in topic_lower for word in ['nature', 'environment', 'climate', 'ecology', 'sustainability', 'green', 'earth', 'planet']):
            return 'nature'
        # Space & Astronomy
        elif any(word in topic_lower for word in ['space', 'astronomy', 'planet', 'galaxy', 'universe', 'cosmos', 'star', 'moon']):
            return 'space'
        else:
            return 'general'