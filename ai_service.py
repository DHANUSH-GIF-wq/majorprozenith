import google.generativeai as genai
import logging
from typing import Optional, Dict, Any, List
import requests
from config import Config

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
    
    def generate_response(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate response from AI model with retry logic
        
        Args:
            prompt: User input prompt
            max_retries: Maximum number of retry attempts
            
        Returns:
            AI generated response
        """
        for attempt in range(max_retries):
            try:
                if not self.model:
                    raise ValueError("Model not initialized")
                
                response = self.model.generate_content(prompt)
                
                if response and hasattr(response, 'text'):
                    logger.info(f"AI response generated successfully (attempt {attempt + 1})")
                    return response.text
                else:
                    raise ValueError("Empty or invalid response from model")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
                
                # Wait before retrying (exponential backoff)
                import time
                time.sleep(2 ** attempt)
        
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
        num_slides: int = 6,
        avoid_text: Optional[str] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate a high-quality explainer with structured slides in NotebookLM style:
        [{ title, bullets[], narration, examples[], visual_prompts[] }]
        """
        constraints = (
            f"Avoid repeating the following text and produce novel explanations: {avoid_text[:800]}"
            if avoid_text else ""
        )
        
        # Adapt slide count based on topic complexity
        topic_words = len(topic.split())
        if topic_words <= 3:
            # Simple topic - fewer slides, more focused
            num_slides = min(4, num_slides)
            focus_instruction = "Keep explanations very simple and focused. Use concrete examples."
        elif topic_words <= 6:
            # Medium topic - balanced approach
            num_slides = min(5, num_slides)
            focus_instruction = "Provide clear, step-by-step explanations with practical examples."
        else:
            # Complex topic - more comprehensive
            num_slides = min(6, num_slides)
            focus_instruction = "Break down complex concepts into digestible parts with clear examples."
        
        prompt = f"""
You are a master educator like NotebookLM. Create a clear, focused explainer for the topic: "{topic}".
Audience level: {level}. Target {num_slides} slides.

CRITICAL STYLE RULES - NEVER VIOLATE:
- NEVER use question marks (?) anywhere in any content
- NEVER start sentences with "What", "How", "Why", "When", "Where", "Which"
- Write ONLY clear, declarative statements
- Use simple, direct language
- Focus on understanding, not memorization
- Make each slide build on the previous one
- Avoid jargon and complex terminology
- Write like explaining to a friend

Each slide must include:
- title: short, clear statement (max 6 words, no questions)
- bullets: 2-3 key points only (max 5 words each, simple statements)
- narration: 40-80 words of flowing explanation that TEACHES the concept clearly
- examples: 1 simple, concrete example that makes the concept clear
- visual_prompts: 1 short prompt describing a simple visual/diagram

Content Guidelines:
- {focus_instruction}
- Start with what the topic IS, not what it isn't
- Use positive, clear language
- Provide practical, real-world context
- End with a clear takeaway or summary

{constraints}

Return ONLY valid JSON with this exact shape:
{{
  "topic": "...",
  "level": "...",
  "slides": [
    {{"title": "...", "bullets": ["..."], "narration": "...", "examples": ["..."], "visual_prompts": ["..."]}}
  ]
}}
Do not include markdown fences or any text outside JSON.
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
        
        # Convert questions to statements - MORE AGGRESSIVE
        question_starters = [
            "What is", "How does", "Why do", "When do", "Where do", "Which is",
            "What are", "How are", "Why are", "When are", "Where are", "Which are",
            "What", "How", "Why", "When", "Where", "Which"
        ]
        
        for starter in question_starters:
            if text.startswith(starter):
                # Convert question to statement
                if starter == "What is":
                    text = text.replace("What is", "This is", 1)
                elif starter == "How does":
                    text = text.replace("How does", "This works by", 1)
                elif starter == "Why do":
                    text = text.replace("Why do", "This happens because", 1)
                elif starter == "When do":
                    text = text.replace("When do", "This occurs when", 1)
                elif starter == "Where do":
                    text = text.replace("Where do", "This happens in", 1)
                elif starter == "Which is":
                    text = text.replace("Which is", "This is", 1)
                elif starter == "What are":
                    text = text.replace("What are", "These are", 1)
                elif starter == "How are":
                    text = text.replace("How are", "These work by", 1)
                elif starter == "Why are":
                    text = text.replace("Why are", "These exist because", 1)
                elif starter == "When are":
                    text = text.replace("When are", "These occur when", 1)
                elif starter == "Where are":
                    text = text.replace("Where are", "These exist in", 1)
                elif starter == "Which are":
                    text = text.replace("Which are", "These are", 1)
                elif starter == "What":
                    text = text.replace("What", "This", 1)
                elif starter == "How":
                    text = text.replace("How", "This works by", 1)
                elif starter == "Why":
                    text = text.replace("Why", "This happens because", 1)
                elif starter == "When":
                    text = text.replace("When", "This occurs when", 1)
                elif starter == "Where":
                    text = text.replace("Where", "This happens in", 1)
                elif starter == "Which":
                    text = text.replace("Which", "This", 1)
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', ':')):
            text = text + '.'
        
        return text

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