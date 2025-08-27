import json
import tempfile
import os
from typing import Dict, List, Any, Optional
import logging
from config import Config
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotesGenerator:
    """Generates comprehensive study notes from topics and concepts"""
    
    def __init__(self):
        self.config = Config()
        self.note_templates = {
            "comprehensive": self._comprehensive_template,
            "summary": self._summary_template,
            "flashcards": self._flashcards_template,
            "study_guide": self._study_guide_template
        }
    
    def generate_notes(self, topic: str, ai_service, note_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate study notes for a topic"""
        try:
            if note_type not in self.note_templates:
                note_type = "comprehensive"
            
            template_func = self.note_templates[note_type]
            return template_func(topic, ai_service)
            
        except Exception as e:
            logger.error(f"Failed to generate notes: {e}")
            return self._create_fallback_notes(topic)
    
    def _comprehensive_template(self, topic: str, ai_service) -> Dict[str, Any]:
        """Generate comprehensive study notes"""
        try:
            prompt = f"""
Create comprehensive study notes for: "{topic}"

Generate detailed notes with the following structure:
- Overview and introduction
- Key concepts and definitions
- Important principles and theories
- Examples and applications
- Common misconceptions
- Study tips and strategies
- Practice questions
- Summary and key takeaways

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "generated_at": "timestamp",
  "note_type": "comprehensive",
  "sections": [
    {{
      "title": "Section Title",
      "content": "Detailed content with bullet points and explanations",
      "key_points": ["Point 1", "Point 2", "Point 3"],
      "examples": ["Example 1", "Example 2"],
      "tips": ["Tip 1", "Tip 2"]
    }}
  ],
  "summary": "Overall summary of the topic",
  "key_terms": ["Term 1", "Term 2", "Term 3"],
  "practice_questions": [
    {{
      "question": "Question text",
      "answer": "Answer text",
      "explanation": "Detailed explanation"
    }}
  ]
}}

Use clear, educational language. Focus on understanding and retention.
"""
            
            response = ai_service.generate_response(prompt)
            
            # Try to extract JSON from response
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    data["generated_at"] = datetime.now().isoformat()
                    return data
            except:
                pass
            
            return self._create_fallback_notes(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive notes: {e}")
            return self._create_fallback_notes(topic)
    
    def _summary_template(self, topic: str, ai_service) -> Dict[str, Any]:
        """Generate summary notes"""
        try:
            prompt = f"""
Create a concise summary of: "{topic}"

Generate a brief but comprehensive summary with:
- Main concepts
- Key points
- Essential definitions
- Quick reference

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "generated_at": "timestamp",
  "note_type": "summary",
  "overview": "Brief overview of the topic",
  "key_concepts": ["Concept 1", "Concept 2", "Concept 3"],
  "definitions": [
    {{
      "term": "Term name",
      "definition": "Clear definition"
    }}
  ],
  "main_points": ["Point 1", "Point 2", "Point 3"],
  "quick_tips": ["Tip 1", "Tip 2"]
}}

Keep it concise and focused on the most important information.
"""
            
            response = ai_service.generate_response(prompt)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    data["generated_at"] = datetime.now().isoformat()
                    return data
            except:
                pass
            
            return self._create_fallback_summary(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate summary notes: {e}")
            return self._create_fallback_summary(topic)
    
    def _flashcards_template(self, topic: str, ai_service) -> Dict[str, Any]:
        """Generate flashcard notes"""
        try:
            prompt = f"""
Create flashcards for: "{topic}"

Generate 10-15 flashcards covering:
- Key concepts and definitions
- Important principles
- Examples and applications
- Common questions

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "generated_at": "timestamp",
  "note_type": "flashcards",
  "flashcards": [
    {{
      "front": "Question or concept",
      "back": "Answer or explanation",
      "category": "Concept/Definition/Example/Question"
    }}
  ],
  "categories": ["Concept", "Definition", "Example", "Question"],
  "study_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Create clear, concise flashcards that are easy to study.
"""
            
            response = ai_service.generate_response(prompt)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    data["generated_at"] = datetime.now().isoformat()
                    return data
            except:
                pass
            
            return self._create_fallback_flashcards(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate flashcard notes: {e}")
            return self._create_fallback_flashcards(topic)
    
    def _study_guide_template(self, topic: str, ai_service) -> Dict[str, Any]:
        """Generate study guide notes"""
        try:
            prompt = f"""
Create a study guide for: "{topic}"

Generate a structured study guide with:
- Learning objectives
- Prerequisites
- Step-by-step learning path
- Practice exercises
- Assessment questions
- Resources for further study

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "generated_at": "timestamp",
  "note_type": "study_guide",
  "learning_objectives": ["Objective 1", "Objective 2", "Objective 3"],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "learning_path": [
    {{
      "step": 1,
      "title": "Step title",
      "description": "What to learn in this step",
      "duration": "Estimated time",
      "resources": ["Resource 1", "Resource 2"]
    }}
  ],
  "practice_exercises": [
    {{
      "title": "Exercise title",
      "description": "Exercise description",
      "solution": "Solution or answer"
    }}
  ],
  "assessment": [
    {{
      "question": "Assessment question",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "Correct option",
      "explanation": "Why this is correct"
    }}
  ],
  "further_resources": ["Resource 1", "Resource 2", "Resource 3"]
}}

Create a practical, actionable study guide.
"""
            
            response = ai_service.generate_response(prompt)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    data["generated_at"] = datetime.now().isoformat()
                    return data
            except:
                pass
            
            return self._create_fallback_study_guide(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate study guide: {e}")
            return self._create_fallback_study_guide(topic)
    
    def _create_fallback_notes(self, topic: str) -> Dict[str, Any]:
        """Create fallback comprehensive notes"""
        return {
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "note_type": "comprehensive",
            "sections": [
                {
                    "title": "Overview",
                    "content": f"{topic} is an important concept that covers fundamental principles and applications.",
                    "key_points": ["Core concept", "Main principles", "Key applications"],
                    "examples": ["Real-world example 1", "Real-world example 2"],
                    "tips": ["Focus on understanding the basics", "Practice regularly"]
                },
                {
                    "title": "Key Concepts",
                    "content": "Understanding the main concepts is essential for mastery of this topic.",
                    "key_points": ["Concept 1", "Concept 2", "Concept 3"],
                    "examples": ["Example 1", "Example 2"],
                    "tips": ["Review concepts regularly", "Connect related ideas"]
                }
            ],
            "summary": f"{topic} encompasses important principles and applications that are valuable to understand.",
            "key_terms": ["Term 1", "Term 2", "Term 3"],
            "practice_questions": [
                {
                    "question": f"What is the main concept of {topic}?",
                    "answer": "The main concept involves understanding the fundamental principles.",
                    "explanation": "This concept forms the foundation for all related applications."
                }
            ]
        }
    
    def _create_fallback_summary(self, topic: str) -> Dict[str, Any]:
        """Create fallback summary notes"""
        return {
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "note_type": "summary",
            "overview": f"{topic} is a fundamental concept with important applications.",
            "key_concepts": ["Core principle", "Main application", "Key benefit"],
            "definitions": [
                {"term": "Main term", "definition": "Clear definition of the main concept"}
            ],
            "main_points": ["Point 1", "Point 2", "Point 3"],
            "quick_tips": ["Study regularly", "Practice applications"]
        }
    
    def _create_fallback_flashcards(self, topic: str) -> Dict[str, Any]:
        """Create fallback flashcard notes"""
        return {
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "note_type": "flashcards",
            "flashcards": [
                {
                    "front": f"What is {topic}?",
                    "back": f"{topic} is a fundamental concept with important applications.",
                    "category": "Definition"
                },
                {
                    "front": "What are the main principles?",
                    "back": "The main principles include understanding core concepts and applications.",
                    "category": "Concept"
                }
            ],
            "categories": ["Concept", "Definition", "Example", "Question"],
            "study_tips": ["Review regularly", "Test yourself", "Practice applications"]
        }
    
    def _create_fallback_study_guide(self, topic: str) -> Dict[str, Any]:
        """Create fallback study guide"""
        return {
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "note_type": "study_guide",
            "learning_objectives": ["Understand core concepts", "Apply principles", "Master applications"],
            "prerequisites": ["Basic knowledge", "Fundamental understanding"],
            "learning_path": [
                {
                    "step": 1,
                    "title": "Introduction",
                    "description": "Learn the basic concepts and principles",
                    "duration": "30 minutes",
                    "resources": ["Basic reading", "Overview video"]
                }
            ],
            "practice_exercises": [
                {
                    "title": "Basic Application",
                    "description": "Apply the concepts to a simple problem",
                    "solution": "Step-by-step solution approach"
                }
            ],
            "assessment": [
                {
                    "question": f"What is the primary purpose of {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "This is correct because it represents the main purpose."
                }
            ],
            "further_resources": ["Advanced reading", "Practice problems", "Related topics"]
        }
    
    def export_notes_to_markdown(self, notes_data: Dict[str, Any], output_path: str = None) -> str:
        """Export notes to Markdown format"""
        try:
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
                output_path = temp_file.name
                temp_file.close()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"# {notes_data.get('topic', 'Study Notes')}\n\n")
                f.write(f"**Generated:** {notes_data.get('generated_at', 'Unknown')}\n")
                f.write(f"**Type:** {notes_data.get('note_type', 'Notes')}\n\n")
                
                note_type = notes_data.get('note_type', 'comprehensive')
                
                if note_type == 'comprehensive':
                    self._write_comprehensive_markdown(f, notes_data)
                elif note_type == 'summary':
                    self._write_summary_markdown(f, notes_data)
                elif note_type == 'flashcards':
                    self._write_flashcards_markdown(f, notes_data)
                elif note_type == 'study_guide':
                    self._write_study_guide_markdown(f, notes_data)
            
            logger.info(f"Notes exported to Markdown: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export notes to Markdown: {e}")
            raise
    
    def _write_comprehensive_markdown(self, f, notes_data):
        """Write comprehensive notes to Markdown"""
        # Write sections
        for section in notes_data.get('sections', []):
            f.write(f"## {section.get('title', 'Section')}\n\n")
            f.write(f"{section.get('content', '')}\n\n")
            
            # Key points
            if section.get('key_points'):
                f.write("**Key Points:**\n")
                for point in section['key_points']:
                    f.write(f"- {point}\n")
                f.write("\n")
            
            # Examples
            if section.get('examples'):
                f.write("**Examples:**\n")
                for example in section['examples']:
                    f.write(f"- {example}\n")
                f.write("\n")
            
            # Tips
            if section.get('tips'):
                f.write("**Tips:**\n")
                for tip in section['tips']:
                    f.write(f"- {tip}\n")
                f.write("\n")
        
        # Summary
        if notes_data.get('summary'):
            f.write(f"## Summary\n\n{notes_data['summary']}\n\n")
        
        # Key terms
        if notes_data.get('key_terms'):
            f.write("## Key Terms\n\n")
            for term in notes_data['key_terms']:
                f.write(f"- **{term}**\n")
            f.write("\n")
        
        # Practice questions
        if notes_data.get('practice_questions'):
            f.write("## Practice Questions\n\n")
            for i, q in enumerate(notes_data['practice_questions'], 1):
                f.write(f"### Question {i}\n")
                f.write(f"{q.get('question', '')}\n\n")
                f.write(f"**Answer:** {q.get('answer', '')}\n\n")
                f.write(f"**Explanation:** {q.get('explanation', '')}\n\n")
    
    def _write_summary_markdown(self, f, notes_data):
        """Write summary notes to Markdown"""
        f.write(f"## Overview\n\n{notes_data.get('overview', '')}\n\n")
        
        if notes_data.get('key_concepts'):
            f.write("## Key Concepts\n\n")
            for concept in notes_data['key_concepts']:
                f.write(f"- {concept}\n")
            f.write("\n")
        
        if notes_data.get('definitions'):
            f.write("## Definitions\n\n")
            for definition in notes_data['definitions']:
                f.write(f"- **{definition.get('term', '')}**: {definition.get('definition', '')}\n")
            f.write("\n")
        
        if notes_data.get('main_points'):
            f.write("## Main Points\n\n")
            for point in notes_data['main_points']:
                f.write(f"- {point}\n")
            f.write("\n")
        
        if notes_data.get('quick_tips'):
            f.write("## Quick Tips\n\n")
            for tip in notes_data['quick_tips']:
                f.write(f"- {tip}\n")
            f.write("\n")
    
    def _write_flashcards_markdown(self, f, notes_data):
        """Write flashcard notes to Markdown"""
        f.write("## Flashcards\n\n")
        
        categories = notes_data.get('categories', [])
        flashcards = notes_data.get('flashcards', [])
        
        for category in categories:
            category_cards = [card for card in flashcards if card.get('category') == category]
            if category_cards:
                f.write(f"### {category}\n\n")
                for i, card in enumerate(category_cards, 1):
                    f.write(f"**Card {i}**\n")
                    f.write(f"**Front:** {card.get('front', '')}\n")
                    f.write(f"**Back:** {card.get('back', '')}\n\n")
        
        if notes_data.get('study_tips'):
            f.write("## Study Tips\n\n")
            for tip in notes_data['study_tips']:
                f.write(f"- {tip}\n")
            f.write("\n")
    
    def _write_study_guide_markdown(self, f, notes_data):
        """Write study guide to Markdown"""
        if notes_data.get('learning_objectives'):
            f.write("## Learning Objectives\n\n")
            for objective in notes_data['learning_objectives']:
                f.write(f"- {objective}\n")
            f.write("\n")
        
        if notes_data.get('prerequisites'):
            f.write("## Prerequisites\n\n")
            for prereq in notes_data['prerequisites']:
                f.write(f"- {prereq}\n")
            f.write("\n")
        
        if notes_data.get('learning_path'):
            f.write("## Learning Path\n\n")
            for step in notes_data['learning_path']:
                f.write(f"### Step {step.get('step', '')}: {step.get('title', '')}\n")
                f.write(f"{step.get('description', '')}\n")
                f.write(f"**Duration:** {step.get('duration', '')}\n")
                if step.get('resources'):
                    f.write("**Resources:**\n")
                    for resource in step['resources']:
                        f.write(f"- {resource}\n")
                f.write("\n")
        
        if notes_data.get('practice_exercises'):
            f.write("## Practice Exercises\n\n")
            for i, exercise in enumerate(notes_data['practice_exercises'], 1):
                f.write(f"### Exercise {i}: {exercise.get('title', '')}\n")
                f.write(f"{exercise.get('description', '')}\n\n")
                f.write(f"**Solution:** {exercise.get('solution', '')}\n\n")
        
        if notes_data.get('assessment'):
            f.write("## Assessment\n\n")
            for i, question in enumerate(notes_data['assessment'], 1):
                f.write(f"### Question {i}\n")
                f.write(f"{question.get('question', '')}\n\n")
                options = question.get('options', [])
                for j, option in enumerate(options):
                    f.write(f"{chr(65+j)}. {option}\n")
                f.write(f"\n**Correct Answer:** {question.get('correct_answer', '')}\n")
                f.write(f"**Explanation:** {question.get('explanation', '')}\n\n")
        
        if notes_data.get('further_resources'):
            f.write("## Further Resources\n\n")
            for resource in notes_data['further_resources']:
                f.write(f"- {resource}\n")
            f.write("\n") 