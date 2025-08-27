import json
import tempfile
import os
from typing import Dict, List, Any, Optional
import logging
from config import Config
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuizGenerator:
    """Generates interactive quizzes from topics and concepts"""
    
    def __init__(self):
        self.config = Config()
        self.quiz_types = {
            "multiple_choice": self._generate_multiple_choice,
            "true_false": self._generate_true_false,
            "fill_blank": self._generate_fill_blank,
            "matching": self._generate_matching,
            "essay": self._generate_essay
        }
    
    def generate_quiz(self, topic: str, ai_service, quiz_type: str = "multiple_choice", 
                     num_questions: int = 10, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate a quiz for a topic"""
        try:
            if quiz_type not in self.quiz_types:
                quiz_type = "multiple_choice"
            
            quiz_func = self.quiz_types[quiz_type]
            return quiz_func(topic, ai_service, num_questions, difficulty)
            
        except Exception as e:
            logger.error(f"Failed to generate quiz: {e}")
            return self._create_fallback_quiz(topic, quiz_type, num_questions)
    
    def _generate_multiple_choice(self, topic: str, ai_service, num_questions: int, difficulty: str) -> Dict[str, Any]:
        """Generate multiple choice quiz"""
        try:
            prompt = f"""
Create a {difficulty} difficulty multiple choice quiz for: "{topic}"

Generate {num_questions} questions with:
- Clear, unambiguous questions
- 4 answer options (A, B, C, D)
- Only one correct answer per question
- Plausible distractors (wrong answers)
- Detailed explanations for correct answers
- Educational value and learning objectives

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "quiz_type": "multiple_choice",
  "difficulty": "{difficulty}",
  "num_questions": {num_questions},
  "generated_at": "timestamp",
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "A",
      "explanation": "Detailed explanation of why this is correct",
      "category": "Concept/Application/Analysis"
    }}
  ],
  "scoring": {{
    "points_per_question": 1,
    "passing_score": 70,
    "time_limit": null
  }},
  "instructions": "Clear instructions for taking the quiz"
}}

Focus on testing understanding and application of concepts.
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
            
            return self._create_fallback_multiple_choice(topic, num_questions)
            
        except Exception as e:
            logger.error(f"Failed to generate multiple choice quiz: {e}")
            return self._create_fallback_multiple_choice(topic, num_questions)
    
    def _generate_true_false(self, topic: str, ai_service, num_questions: int, difficulty: str) -> Dict[str, Any]:
        """Generate true/false quiz"""
        try:
            prompt = f"""
Create a {difficulty} difficulty true/false quiz for: "{topic}"

Generate {num_questions} statements with:
- Clear, factual statements
- Mix of true and false statements
- Educational value
- Detailed explanations for each answer
- Focus on common misconceptions

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "quiz_type": "true_false",
  "difficulty": "{difficulty}",
  "num_questions": {num_questions},
  "generated_at": "timestamp",
  "questions": [
    {{
      "statement": "Statement to evaluate",
      "correct_answer": true,
      "explanation": "Detailed explanation of why this is true/false",
      "category": "Concept/Fact/Misconception"
    }}
  ],
  "scoring": {{
    "points_per_question": 1,
    "passing_score": 70,
    "time_limit": null
  }},
  "instructions": "Instructions for the true/false quiz"
}}

Focus on testing knowledge and identifying misconceptions.
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
            
            return self._create_fallback_true_false(topic, num_questions)
            
        except Exception as e:
            logger.error(f"Failed to generate true/false quiz: {e}")
            return self._create_fallback_true_false(topic, num_questions)
    
    def _generate_fill_blank(self, topic: str, ai_service, num_questions: int, difficulty: str) -> Dict[str, Any]:
        """Generate fill-in-the-blank quiz"""
        try:
            prompt = f"""
Create a {difficulty} difficulty fill-in-the-blank quiz for: "{topic}"

Generate {num_questions} questions with:
- Sentences with key terms removed
- Clear context clues
- Multiple acceptable answers where appropriate
- Detailed explanations
- Educational focus

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "quiz_type": "fill_blank",
  "difficulty": "{difficulty}",
  "num_questions": {num_questions},
  "generated_at": "timestamp",
  "questions": [
    {{
      "sentence": "The _____ is a key concept in this field.",
      "correct_answers": ["concept", "principle", "element"],
      "explanation": "Explanation of the correct answer",
      "category": "Term/Concept/Definition"
    }}
  ],
  "scoring": {{
    "points_per_question": 1,
    "passing_score": 70,
    "time_limit": null
  }},
  "instructions": "Instructions for fill-in-the-blank quiz"
}}

Focus on testing vocabulary and key concepts.
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
            
            return self._create_fallback_fill_blank(topic, num_questions)
            
        except Exception as e:
            logger.error(f"Failed to generate fill-in-the-blank quiz: {e}")
            return self._create_fallback_fill_blank(topic, num_questions)
    
    def _generate_matching(self, topic: str, ai_service, num_questions: int, difficulty: str) -> Dict[str, Any]:
        """Generate matching quiz"""
        try:
            prompt = f"""
Create a {difficulty} difficulty matching quiz for: "{topic}"

Generate matching pairs with:
- Clear terms and definitions
- Logical relationships
- Educational value
- Detailed explanations
- Appropriate difficulty level

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "quiz_type": "matching",
  "difficulty": "{difficulty}",
  "num_questions": {num_questions},
  "generated_at": "timestamp",
  "items": [
    {{
      "term": "Term or concept",
      "definition": "Corresponding definition or description",
      "explanation": "Detailed explanation of the relationship",
      "category": "Concept/Process/Application"
    }}
  ],
  "scoring": {{
    "points_per_match": 1,
    "passing_score": 70,
    "time_limit": null
  }},
  "instructions": "Instructions for matching quiz"
}}

Focus on testing understanding of relationships and definitions.
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
            
            return self._create_fallback_matching(topic, num_questions)
            
        except Exception as e:
            logger.error(f"Failed to generate matching quiz: {e}")
            return self._create_fallback_matching(topic, num_questions)
    
    def _generate_essay(self, topic: str, ai_service, num_questions: int, difficulty: str) -> Dict[str, Any]:
        """Generate essay questions"""
        try:
            prompt = f"""
Create {difficulty} difficulty essay questions for: "{topic}"

Generate {num_questions} essay prompts with:
- Thought-provoking questions
- Clear evaluation criteria
- Suggested response length
- Key points to address
- Educational objectives

Return ONLY valid JSON with this structure:
{{
  "topic": "Topic Name",
  "quiz_type": "essay",
  "difficulty": "{difficulty}",
  "num_questions": {num_questions},
  "generated_at": "timestamp",
  "questions": [
    {{
      "prompt": "Essay question or prompt",
      "suggested_length": "2-3 paragraphs",
      "key_points": ["Point 1", "Point 2", "Point 3"],
      "evaluation_criteria": ["Criterion 1", "Criterion 2", "Criterion 3"],
      "category": "Analysis/Synthesis/Application"
    }}
  ],
  "scoring": {{
    "points_per_question": 10,
    "passing_score": 70,
    "time_limit": null
  }},
  "instructions": "Instructions for essay questions"
}}

Focus on testing critical thinking and deep understanding.
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
            
            return self._create_fallback_essay(topic, num_questions)
            
        except Exception as e:
            logger.error(f"Failed to generate essay questions: {e}")
            return self._create_fallback_essay(topic, num_questions)
    
    def _create_fallback_multiple_choice(self, topic: str, num_questions: int) -> Dict[str, Any]:
        """Create fallback multiple choice quiz"""
        questions = []
        for i in range(min(num_questions, 5)):
            questions.append({
                "question": f"What is a key concept related to {topic}?",
                "options": [
                    "A fundamental principle",
                    "An advanced technique", 
                    "A basic application",
                    "A complex theory"
                ],
                "correct_answer": "A",
                "explanation": "This represents the most fundamental understanding of the concept.",
                "category": "Concept"
            })
        
        return {
            "topic": topic,
            "quiz_type": "multiple_choice",
            "difficulty": "medium",
            "num_questions": len(questions),
            "generated_at": datetime.now().isoformat(),
            "questions": questions,
            "scoring": {
                "points_per_question": 1,
                "passing_score": 70,
                "time_limit": None
            },
            "instructions": f"Answer {len(questions)} multiple choice questions about {topic}. Select the best answer for each question."
        }
    
    def _create_fallback_true_false(self, topic: str, num_questions: int) -> Dict[str, Any]:
        """Create fallback true/false quiz"""
        questions = []
        for i in range(min(num_questions, 5)):
            questions.append({
                "statement": f"{topic} is an important concept in this field.",
                "correct_answer": True,
                "explanation": "This statement is true as it represents a fundamental understanding.",
                "category": "Fact"
            })
        
        return {
            "topic": topic,
            "quiz_type": "true_false",
            "difficulty": "medium",
            "num_questions": len(questions),
            "generated_at": datetime.now().isoformat(),
            "questions": questions,
            "scoring": {
                "points_per_question": 1,
                "passing_score": 70,
                "time_limit": None
            },
            "instructions": f"Determine if {len(questions)} statements about {topic} are true or false."
        }
    
    def _create_fallback_fill_blank(self, topic: str, num_questions: int) -> Dict[str, Any]:
        """Create fallback fill-in-the-blank quiz"""
        questions = []
        for i in range(min(num_questions, 5)):
            questions.append({
                "sentence": f"The _____ is a key concept in {topic}.",
                "correct_answers": ["concept", "principle", "element"],
                "explanation": "This blank should be filled with a key term related to the topic.",
                "category": "Term"
            })
        
        return {
            "topic": topic,
            "quiz_type": "fill_blank",
            "difficulty": "medium",
            "num_questions": len(questions),
            "generated_at": datetime.now().isoformat(),
            "questions": questions,
            "scoring": {
                "points_per_question": 1,
                "passing_score": 70,
                "time_limit": None
            },
            "instructions": f"Fill in the blanks in {len(questions)} sentences about {topic}."
        }
    
    def _create_fallback_matching(self, topic: str, num_questions: int) -> Dict[str, Any]:
        """Create fallback matching quiz"""
        items = []
        for i in range(min(num_questions, 5)):
            items.append({
                "term": f"Term {i+1}",
                "definition": f"Definition for term {i+1}",
                "explanation": f"This term relates to {topic} in the following way.",
                "category": "Concept"
            })
        
        return {
            "topic": topic,
            "quiz_type": "matching",
            "difficulty": "medium",
            "num_questions": len(items),
            "generated_at": datetime.now().isoformat(),
            "items": items,
            "scoring": {
                "points_per_match": 1,
                "passing_score": 70,
                "time_limit": None
            },
            "instructions": f"Match {len(items)} terms with their definitions related to {topic}."
        }
    
    def _create_fallback_essay(self, topic: str, num_questions: int) -> Dict[str, Any]:
        """Create fallback essay questions"""
        questions = []
        for i in range(min(num_questions, 3)):
            questions.append({
                "prompt": f"Explain the importance of {topic} in this field.",
                "suggested_length": "2-3 paragraphs",
                "key_points": ["Definition", "Importance", "Applications"],
                "evaluation_criteria": ["Clarity", "Completeness", "Accuracy"],
                "category": "Analysis"
            })
        
        return {
            "topic": topic,
            "quiz_type": "essay",
            "difficulty": "medium",
            "num_questions": len(questions),
            "generated_at": datetime.now().isoformat(),
            "questions": questions,
            "scoring": {
                "points_per_question": 10,
                "passing_score": 70,
                "time_limit": None
            },
            "instructions": f"Answer {len(questions)} essay questions about {topic}. Provide detailed, well-structured responses."
        }
    
    def _create_fallback_quiz(self, topic: str, quiz_type: str, num_questions: int) -> Dict[str, Any]:
        """Create generic fallback quiz"""
        return {
            "topic": topic,
            "quiz_type": quiz_type,
            "difficulty": "medium",
            "num_questions": num_questions,
            "generated_at": datetime.now().isoformat(),
            "questions": [],
            "scoring": {
                "points_per_question": 1,
                "passing_score": 70,
                "time_limit": None
            },
            "instructions": f"Complete the {quiz_type} quiz about {topic}."
        }
    
    def grade_quiz(self, quiz_data: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a completed quiz"""
        try:
            quiz_type = quiz_data.get("quiz_type", "multiple_choice")
            questions = quiz_data.get("questions", [])
            items = quiz_data.get("items", [])  # For matching quizzes
            
            total_questions = len(questions) if questions else len(items)
            correct_answers = 0
            detailed_results = []
            
            if quiz_type == "multiple_choice":
                for i, question in enumerate(questions):
                    user_answer = answers.get(str(i), "")
                    correct = user_answer.upper() == question.get("correct_answer", "")
                    if correct:
                        correct_answers += 1
                    
                    detailed_results.append({
                        "question": question.get("question", ""),
                        "user_answer": user_answer,
                        "correct_answer": question.get("correct_answer", ""),
                        "correct": correct,
                        "explanation": question.get("explanation", "")
                    })
            
            elif quiz_type == "true_false":
                for i, question in enumerate(questions):
                    user_answer = answers.get(str(i), False)
                    correct = user_answer == question.get("correct_answer", False)
                    if correct:
                        correct_answers += 1
                    
                    detailed_results.append({
                        "statement": question.get("statement", ""),
                        "user_answer": user_answer,
                        "correct_answer": question.get("correct_answer", False),
                        "correct": correct,
                        "explanation": question.get("explanation", "")
                    })
            
            elif quiz_type == "fill_blank":
                for i, question in enumerate(questions):
                    user_answer = answers.get(str(i), "").strip().lower()
                    correct_answers_list = [ans.lower() for ans in question.get("correct_answers", [])]
                    correct = user_answer in correct_answers_list
                    if correct:
                        correct_answers += 1
                    
                    detailed_results.append({
                        "sentence": question.get("sentence", ""),
                        "user_answer": user_answer,
                        "correct_answers": correct_answers_list,
                        "correct": correct,
                        "explanation": question.get("explanation", "")
                    })
            
            elif quiz_type == "matching":
                for i, item in enumerate(items):
                    user_answer = answers.get(str(i), "")
                    correct_answer = item.get("definition", "")
                    correct = user_answer.strip().lower() == correct_answer.strip().lower()
                    if correct:
                        correct_answers += 1
                    
                    detailed_results.append({
                        "term": item.get("term", ""),
                        "user_answer": user_answer,
                        "correct_answer": correct_answer,
                        "correct": correct,
                        "explanation": item.get("explanation", "")
                    })
            
            # Calculate score
            score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            passing_score = quiz_data.get("scoring", {}).get("passing_score", 70)
            passed = score_percentage >= passing_score
            
            return {
                "quiz_topic": quiz_data.get("topic", ""),
                "quiz_type": quiz_type,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "score_percentage": round(score_percentage, 2),
                "passed": passed,
                "passing_score": passing_score,
                "detailed_results": detailed_results,
                "feedback": self._generate_feedback(score_percentage, quiz_type),
                "graded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to grade quiz: {e}")
            raise
    
    def _generate_feedback(self, score_percentage: float, quiz_type: str) -> str:
        """Generate feedback based on quiz performance"""
        if score_percentage >= 90:
            return f"Excellent work! You scored {score_percentage}% on this {quiz_type} quiz. You have a strong understanding of the material."
        elif score_percentage >= 80:
            return f"Good job! You scored {score_percentage}% on this {quiz_type} quiz. You have a solid understanding with room for improvement."
        elif score_percentage >= 70:
            return f"Passing score! You scored {score_percentage}% on this {quiz_type} quiz. Review the material to strengthen your understanding."
        elif score_percentage >= 60:
            return f"You scored {score_percentage}% on this {quiz_type} quiz. Focus on reviewing the concepts you missed."
        else:
            return f"You scored {score_percentage}% on this {quiz_type} quiz. Consider reviewing the material thoroughly before retaking."
    
    def export_quiz_to_markdown(self, quiz_data: Dict[str, Any], output_path: str = None) -> str:
        """Export quiz to Markdown format"""
        try:
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
                output_path = temp_file.name
                temp_file.close()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"# {quiz_data.get('topic', 'Quiz')} - {quiz_data.get('quiz_type', 'Quiz').title()}\n\n")
                f.write(f"**Generated:** {quiz_data.get('generated_at', 'Unknown')}\n")
                f.write(f"**Difficulty:** {quiz_data.get('difficulty', 'Medium')}\n")
                f.write(f"**Questions:** {quiz_data.get('num_questions', 0)}\n\n")
                
                # Instructions
                if quiz_data.get('instructions'):
                    f.write(f"## Instructions\n\n{quiz_data['instructions']}\n\n")
                
                quiz_type = quiz_data.get('quiz_type', 'multiple_choice')
                
                if quiz_type == 'multiple_choice':
                    self._write_multiple_choice_markdown(f, quiz_data)
                elif quiz_type == 'true_false':
                    self._write_true_false_markdown(f, quiz_data)
                elif quiz_type == 'fill_blank':
                    self._write_fill_blank_markdown(f, quiz_data)
                elif quiz_type == 'matching':
                    self._write_matching_markdown(f, quiz_data)
                elif quiz_type == 'essay':
                    self._write_essay_markdown(f, quiz_data)
                
                # Answer key
                f.write("## Answer Key\n\n")
                f.write("*Answers and explanations for all questions.*\n\n")
                
                if quiz_type == 'multiple_choice':
                    for i, question in enumerate(quiz_data.get('questions', []), 1):
                        f.write(f"**{i}.** {question.get('question', '')}\n")
                        f.write(f"**Answer:** {question.get('correct_answer', '')}\n")
                        f.write(f"**Explanation:** {question.get('explanation', '')}\n\n")
                
                elif quiz_type == 'true_false':
                    for i, question in enumerate(quiz_data.get('questions', []), 1):
                        f.write(f"**{i}.** {question.get('statement', '')}\n")
                        f.write(f"**Answer:** {question.get('correct_answer', '')}\n")
                        f.write(f"**Explanation:** {question.get('explanation', '')}\n\n")
                
                elif quiz_type == 'fill_blank':
                    for i, question in enumerate(quiz_data.get('questions', []), 1):
                        f.write(f"**{i}.** {question.get('sentence', '')}\n")
                        f.write(f"**Answer:** {', '.join(question.get('correct_answers', []))}\n")
                        f.write(f"**Explanation:** {question.get('explanation', '')}\n\n")
                
                elif quiz_type == 'matching':
                    for i, item in enumerate(quiz_data.get('items', []), 1):
                        f.write(f"**{i}.** {item.get('term', '')} → {item.get('definition', '')}\n")
                        f.write(f"**Explanation:** {item.get('explanation', '')}\n\n")
                
                elif quiz_type == 'essay':
                    for i, question in enumerate(quiz_data.get('questions', []), 1):
                        f.write(f"**{i}.** {question.get('prompt', '')}\n")
                        f.write(f"**Key Points:** {', '.join(question.get('key_points', []))}\n")
                        f.write(f"**Evaluation Criteria:** {', '.join(question.get('evaluation_criteria', []))}\n\n")
            
            logger.info(f"Quiz exported to Markdown: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export quiz to Markdown: {e}")
            raise
    
    def _write_multiple_choice_markdown(self, f, quiz_data):
        """Write multiple choice quiz to Markdown"""
        f.write("## Questions\n\n")
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            f.write(f"**{i}.** {question.get('question', '')}\n\n")
            options = question.get('options', [])
            for j, option in enumerate(options):
                f.write(f"   **{chr(65+j)}.** {option}\n")
            f.write("\n")
    
    def _write_true_false_markdown(self, f, quiz_data):
        """Write true/false quiz to Markdown"""
        f.write("## Statements\n\n")
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            f.write(f"**{i}.** {question.get('statement', '')}\n\n")
            f.write("   **True** / **False**\n\n")
    
    def _write_fill_blank_markdown(self, f, quiz_data):
        """Write fill-in-the-blank quiz to Markdown"""
        f.write("## Sentences\n\n")
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            f.write(f"**{i}.** {question.get('sentence', '')}\n\n")
            f.write("   **Answer:** ________________\n\n")
    
    def _write_matching_markdown(self, f, quiz_data):
        """Write matching quiz to Markdown"""
        f.write("## Matching\n\n")
        f.write("Match each term with its definition:\n\n")
        
        items = quiz_data.get('items', [])
        # Shuffle items for quiz
        shuffled_items = items.copy()
        random.shuffle(shuffled_items)
        
        for i, item in enumerate(shuffled_items, 1):
            f.write(f"**{i}.** {item.get('term', '')}\n")
        
        f.write("\n**Definitions:**\n\n")
        definitions = [item.get('definition', '') for item in items]
        random.shuffle(definitions)
        for i, definition in enumerate(definitions, 1):
            f.write(f"**{chr(65+i-1)}.** {definition}\n")
        
        f.write("\n")
    
    def _write_essay_markdown(self, f, quiz_data):
        """Write essay questions to Markdown"""
        f.write("## Essay Questions\n\n")
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            f.write(f"**{i}.** {question.get('prompt', '')}\n\n")
            f.write(f"**Suggested Length:** {question.get('suggested_length', '')}\n\n")
            f.write("**Key Points to Address:**\n")
            for point in question.get('key_points', []):
                f.write(f"- {point}\n")
            f.write("\n")
            f.write("**Evaluation Criteria:**\n")
            for criterion in question.get('evaluation_criteria', []):
                f.write(f"- {criterion}\n")
            f.write("\n") 