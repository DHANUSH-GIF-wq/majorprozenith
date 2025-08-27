import json
import tempfile
import os
from typing import Dict, List, Any, Optional
import logging
from config import Config
from datetime import datetime, timedelta
import calendar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudyPlanner:
    """Generates personalized study plans and schedules"""
    
    def __init__(self):
        self.config = Config()
        self.study_methods = {
            "pomodoro": {"work": 25, "break": 5, "long_break": 15},
            "traditional": {"work": 45, "break": 15, "long_break": 30},
            "intensive": {"work": 60, "break": 10, "long_break": 20},
            "casual": {"work": 30, "break": 10, "long_break": 25}
        }
    
    def generate_study_plan(self, topic: str, ai_service, study_duration: int = 7, 
                           hours_per_day: int = 2, difficulty: str = "medium",
                           study_method: str = "pomodoro") -> Dict[str, Any]:
        """Generate a comprehensive study plan"""
        try:
            # Generate topic breakdown
            topic_breakdown = self._generate_topic_breakdown(topic, ai_service, difficulty)
            
            # Create study schedule
            schedule = self._create_study_schedule(topic_breakdown, study_duration, hours_per_day, study_method)
            
            # Generate learning objectives
            objectives = self._generate_learning_objectives(topic, ai_service, difficulty)
            
            # Create progress tracking
            progress_tracking = self._create_progress_tracking(topic_breakdown, study_duration)
            
            return {
                "topic": topic,
                "generated_at": datetime.now().isoformat(),
                "study_duration": study_duration,
                "hours_per_day": hours_per_day,
                "difficulty": difficulty,
                "study_method": study_method,
                "topic_breakdown": topic_breakdown,
                "schedule": schedule,
                "objectives": objectives,
                "progress_tracking": progress_tracking,
                "study_tips": self._generate_study_tips(study_method),
                "resources": self._generate_resource_list(topic, ai_service)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate study plan: {e}")
            return self._create_fallback_study_plan(topic, study_duration, hours_per_day)
    
    def _generate_topic_breakdown(self, topic: str, ai_service, difficulty: str) -> List[Dict[str, Any]]:
        """Generate detailed topic breakdown"""
        try:
            prompt = f"""
Create a detailed breakdown of the topic: "{topic}" for {difficulty} level study.

Break down the topic into:
- Logical learning units
- Estimated study time for each unit
- Prerequisites and dependencies
- Key concepts to master
- Practice activities

Return ONLY valid JSON with this structure:
{{
  "units": [
    {{
      "title": "Unit Title",
      "description": "What this unit covers",
      "estimated_hours": 2,
      "key_concepts": ["Concept 1", "Concept 2"],
      "prerequisites": ["Previous unit or knowledge"],
      "activities": ["Activity 1", "Activity 2"],
      "difficulty": "easy/medium/hard"
    }}
  ]
}}

Structure the units in logical learning order. Consider dependencies between concepts.
"""
            
            response = ai_service.generate_response(prompt)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    return data.get("units", [])
            except:
                pass
            
            return self._create_fallback_topic_breakdown(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate topic breakdown: {e}")
            return self._create_fallback_topic_breakdown(topic)
    
    def _create_fallback_topic_breakdown(self, topic: str) -> List[Dict[str, Any]]:
        """Create fallback topic breakdown"""
        return [
            {
                "title": f"Introduction to {topic}",
                "description": f"Basic concepts and fundamentals of {topic}",
                "estimated_hours": 2,
                "key_concepts": ["Basic principles", "Core concepts", "Fundamental ideas"],
                "prerequisites": ["General knowledge"],
                "activities": ["Reading", "Note-taking", "Basic exercises"],
                "difficulty": "easy"
            },
            {
                "title": f"Core Concepts of {topic}",
                "description": f"Main principles and key components of {topic}",
                "estimated_hours": 3,
                "key_concepts": ["Main principles", "Key components", "Important elements"],
                "prerequisites": [f"Introduction to {topic}"],
                "activities": ["Practice problems", "Concept mapping", "Discussion"],
                "difficulty": "medium"
            },
            {
                "title": f"Applications of {topic}",
                "description": f"Real-world applications and practical uses of {topic}",
                "estimated_hours": 2,
                "key_concepts": ["Practical applications", "Real-world examples", "Use cases"],
                "prerequisites": [f"Core Concepts of {topic}"],
                "activities": ["Case studies", "Projects", "Problem solving"],
                "difficulty": "medium"
            },
            {
                "title": f"Advanced {topic}",
                "description": f"Advanced concepts and complex applications of {topic}",
                "estimated_hours": 3,
                "key_concepts": ["Advanced concepts", "Complex applications", "Deep understanding"],
                "prerequisites": [f"Applications of {topic}"],
                "activities": ["Advanced projects", "Research", "Analysis"],
                "difficulty": "hard"
            }
        ]
    
    def _create_study_schedule(self, topic_breakdown: List[Dict[str, Any]], 
                              study_duration: int, hours_per_day: int, study_method: str) -> Dict[str, Any]:
        """Create detailed study schedule"""
        try:
            total_hours = sum(unit.get("estimated_hours", 1) for unit in topic_breakdown)
            total_days_needed = max(1, total_hours // hours_per_day)
            
            # Adjust study duration if needed
            if total_days_needed > study_duration:
                study_duration = total_days_needed
            
            schedule = {
                "total_hours": total_hours,
                "total_days": study_duration,
                "hours_per_day": hours_per_day,
                "study_method": study_method,
                "method_settings": self.study_methods.get(study_method, self.study_methods["pomodoro"]),
                "daily_schedules": []
            }
            
            # Create daily schedules
            current_unit_index = 0
            current_unit_progress = 0
            
            for day in range(1, study_duration + 1):
                daily_schedule = {
                    "day": day,
                    "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
                    "day_of_week": (datetime.now() + timedelta(days=day-1)).strftime("%A"),
                    "sessions": [],
                    "total_hours": 0
                }
                
                remaining_hours = hours_per_day
                
                while remaining_hours > 0 and current_unit_index < len(topic_breakdown):
                    unit = topic_breakdown[current_unit_index]
                    unit_hours = unit.get("estimated_hours", 1)
                    unit_remaining = unit_hours - current_unit_progress
                    
                    if unit_remaining <= 0:
                        current_unit_index += 1
                        current_unit_progress = 0
                        continue
                    
                    session_hours = min(remaining_hours, unit_remaining)
                    
                    session = {
                        "unit": unit.get("title", ""),
                        "duration": session_hours,
                        "activities": unit.get("activities", []),
                        "key_concepts": unit.get("key_concepts", []),
                        "difficulty": unit.get("difficulty", "medium")
                    }
                    
                    daily_schedule["sessions"].append(session)
                    daily_schedule["total_hours"] += session_hours
                    remaining_hours -= session_hours
                    current_unit_progress += session_hours
                
                schedule["daily_schedules"].append(daily_schedule)
            
            return schedule
            
        except Exception as e:
            logger.error(f"Failed to create study schedule: {e}")
            return self._create_fallback_schedule(study_duration, hours_per_day)
    
    def _create_fallback_schedule(self, study_duration: int, hours_per_day: int) -> Dict[str, Any]:
        """Create fallback study schedule"""
        schedule = {
            "total_hours": study_duration * hours_per_day,
            "total_days": study_duration,
            "hours_per_day": hours_per_day,
            "study_method": "pomodoro",
            "method_settings": self.study_methods["pomodoro"],
            "daily_schedules": []
        }
        
        for day in range(1, study_duration + 1):
            daily_schedule = {
                "day": day,
                "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
                "day_of_week": (datetime.now() + timedelta(days=day-1)).strftime("%A"),
                "sessions": [
                    {
                        "unit": f"Study Session {day}",
                        "duration": hours_per_day,
                        "activities": ["Reading", "Note-taking", "Practice"],
                        "key_concepts": ["Core concepts", "Key principles"],
                        "difficulty": "medium"
                    }
                ],
                "total_hours": hours_per_day
            }
            schedule["daily_schedules"].append(daily_schedule)
        
        return schedule
    
    def _generate_learning_objectives(self, topic: str, ai_service, difficulty: str) -> List[Dict[str, Any]]:
        """Generate learning objectives"""
        try:
            prompt = f"""
Create specific learning objectives for studying: "{topic}" at {difficulty} level.

Generate objectives that are:
- Specific and measurable
- Realistic and achievable
- Time-bound
- Progressive in difficulty

Return ONLY valid JSON with this structure:
{{
  "objectives": [
    {{
      "objective": "Specific learning objective",
      "category": "Knowledge/Understanding/Application/Analysis",
      "difficulty": "easy/medium/hard",
      "timeframe": "1-2 weeks",
      "success_criteria": ["Criterion 1", "Criterion 2"]
    }}
  ]
}}

Focus on creating clear, achievable learning goals.
"""
            
            response = ai_service.generate_response(prompt)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    return data.get("objectives", [])
            except:
                pass
            
            return self._create_fallback_objectives(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate learning objectives: {e}")
            return self._create_fallback_objectives(topic)
    
    def _create_fallback_objectives(self, topic: str) -> List[Dict[str, Any]]:
        """Create fallback learning objectives"""
        return [
            {
                "objective": f"Understand the basic concepts of {topic}",
                "category": "Knowledge",
                "difficulty": "easy",
                "timeframe": "1 week",
                "success_criteria": ["Can define key terms", "Can explain basic principles"]
            },
            {
                "objective": f"Apply {topic} concepts to solve problems",
                "category": "Application",
                "difficulty": "medium",
                "timeframe": "2 weeks",
                "success_criteria": ["Can solve basic problems", "Can apply concepts correctly"]
            },
            {
                "objective": f"Analyze complex {topic} scenarios",
                "category": "Analysis",
                "difficulty": "hard",
                "timeframe": "3 weeks",
                "success_criteria": ["Can analyze complex situations", "Can evaluate different approaches"]
            }
        ]
    
    def _create_progress_tracking(self, topic_breakdown: List[Dict[str, Any]], study_duration: int) -> Dict[str, Any]:
        """Create progress tracking system"""
        total_units = len(topic_breakdown)
        total_hours = sum(unit.get("estimated_hours", 1) for unit in topic_breakdown)
        
        milestones = []
        for i, unit in enumerate(topic_breakdown):
            milestone = {
                "unit": unit.get("title", f"Unit {i+1}"),
                "day_target": max(1, (i + 1) * study_duration // total_units),
                "hours_target": sum(u.get("estimated_hours", 1) for u in topic_breakdown[:i+1]),
                "completed": False,
                "completion_date": None,
                "notes": ""
            }
            milestones.append(milestone)
        
        return {
            "total_units": total_units,
            "total_hours": total_hours,
            "completed_units": 0,
            "completed_hours": 0,
            "progress_percentage": 0,
            "milestones": milestones,
            "daily_log": [],
            "achievements": []
        }
    
    def _generate_study_tips(self, study_method: str) -> List[str]:
        """Generate study tips based on study method"""
        tips = {
            "pomodoro": [
                "Work in focused 25-minute sessions",
                "Take 5-minute breaks between sessions",
                "Take longer 15-minute breaks every 4 sessions",
                "Eliminate distractions during work sessions",
                "Track your completed pomodoros"
            ],
            "traditional": [
                "Study in 45-minute focused blocks",
                "Take 15-minute breaks between sessions",
                "Use longer breaks for complex topics",
                "Review material at the end of each session",
                "Plan your study sessions in advance"
            ],
            "intensive": [
                "Study in 60-minute intensive sessions",
                "Take short 10-minute breaks",
                "Use longer breaks for recovery",
                "Focus on one topic per session",
                "Practice active recall techniques"
            ],
            "casual": [
                "Study in comfortable 30-minute sessions",
                "Take regular 10-minute breaks",
                "Use longer breaks for relaxation",
                "Study at your own pace",
                "Focus on understanding over speed"
            ]
        }
        
        return tips.get(study_method, tips["pomodoro"])
    
    def _generate_resource_list(self, topic: str, ai_service) -> List[Dict[str, Any]]:
        """Generate resource list for studying"""
        try:
            prompt = f"""
Suggest study resources for: "{topic}"

Include different types of resources:
- Books and textbooks
- Online courses and tutorials
- Practice exercises and problems
- Videos and multimedia
- Websites and articles
- Tools and software

Return ONLY valid JSON with this structure:
{{
  "resources": [
    {{
      "title": "Resource Title",
      "type": "book/course/video/website/tool",
      "description": "Brief description of the resource",
      "difficulty": "beginner/intermediate/advanced",
      "url": "URL if applicable",
      "cost": "free/paid",
      "recommended": true
    }}
  ]
}}

Focus on high-quality, educational resources.
"""
            
            response = ai_service.generate_response(prompt)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    return data.get("resources", [])
            except:
                pass
            
            return self._create_fallback_resources(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate resource list: {e}")
            return self._create_fallback_resources(topic)
    
    def _create_fallback_resources(self, topic: str) -> List[Dict[str, Any]]:
        """Create fallback resource list"""
        return [
            {
                "title": f"Introduction to {topic}",
                "type": "book",
                "description": f"Comprehensive textbook covering {topic} fundamentals",
                "difficulty": "beginner",
                "url": "",
                "cost": "paid",
                "recommended": True
            },
            {
                "title": f"{topic} Online Course",
                "type": "course",
                "description": f"Structured online course for learning {topic}",
                "difficulty": "intermediate",
                "url": "https://example.com/course",
                "cost": "free",
                "recommended": True
            },
            {
                "title": f"{topic} Practice Problems",
                "type": "exercises",
                "description": f"Collection of practice problems and exercises",
                "difficulty": "intermediate",
                "url": "",
                "cost": "free",
                "recommended": True
            },
            {
                "title": f"{topic} Video Tutorials",
                "type": "video",
                "description": f"Video tutorials explaining {topic} concepts",
                "difficulty": "beginner",
                "url": "https://example.com/videos",
                "cost": "free",
                "recommended": True
            }
        ]
    
    def _create_fallback_study_plan(self, topic: str, study_duration: int, hours_per_day: int) -> Dict[str, Any]:
        """Create fallback study plan"""
        return {
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "study_duration": study_duration,
            "hours_per_day": hours_per_day,
            "difficulty": "medium",
            "study_method": "pomodoro",
            "topic_breakdown": self._create_fallback_topic_breakdown(topic),
            "schedule": self._create_fallback_schedule(study_duration, hours_per_day),
            "objectives": self._create_fallback_objectives(topic),
            "progress_tracking": self._create_progress_tracking(self._create_fallback_topic_breakdown(topic), study_duration),
            "study_tips": self._generate_study_tips("pomodoro"),
            "resources": self._create_fallback_resources(topic)
        }
    
    def update_progress(self, study_plan: Dict[str, Any], completed_units: List[str], 
                       completed_hours: float, notes: str = "") -> Dict[str, Any]:
        """Update study plan progress"""
        try:
            progress = study_plan.get("progress_tracking", {})
            
            # Update completed units
            for unit_title in completed_units:
                for milestone in progress.get("milestones", []):
                    if milestone["unit"] == unit_title and not milestone["completed"]:
                        milestone["completed"] = True
                        milestone["completion_date"] = datetime.now().isoformat()
                        milestone["notes"] = notes
            
            # Update progress statistics
            completed_milestones = sum(1 for m in progress.get("milestones", []) if m["completed"])
            total_milestones = len(progress.get("milestones", []))
            
            progress["completed_units"] = completed_milestones
            progress["completed_hours"] = completed_hours
            progress["progress_percentage"] = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
            
            # Add daily log entry
            daily_log_entry = {
                "date": datetime.now().isoformat(),
                "completed_units": completed_units,
                "hours_studied": completed_hours,
                "notes": notes
            }
            progress["daily_log"].append(daily_log_entry)
            
            # Check for achievements
            achievements = self._check_achievements(progress)
            progress["achievements"] = achievements
            
            return study_plan
            
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
            return study_plan
    
    def _check_achievements(self, progress: Dict[str, Any]) -> List[str]:
        """Check for study achievements"""
        achievements = []
        
        completed_units = progress.get("completed_units", 0)
        progress_percentage = progress.get("progress_percentage", 0)
        days_studied = len(progress.get("daily_log", []))
        
        if completed_units >= 1:
            achievements.append("First Unit Complete")
        if completed_units >= 2:
            achievements.append("Getting Started")
        if progress_percentage >= 25:
            achievements.append("Quarter Way There")
        if progress_percentage >= 50:
            achievements.append("Halfway Point")
        if progress_percentage >= 75:
            achievements.append("Almost There")
        if progress_percentage >= 100:
            achievements.append("Study Plan Complete")
        if days_studied >= 7:
            achievements.append("Week of Study")
        if days_studied >= 30:
            achievements.append("Month of Dedication")
        
        return achievements
    
    def export_study_plan_to_markdown(self, study_plan: Dict[str, Any], output_path: str = None) -> str:
        """Export study plan to Markdown format"""
        try:
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
                output_path = temp_file.name
                temp_file.close()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"# Study Plan: {study_plan.get('topic', 'Topic')}\n\n")
                f.write(f"**Generated:** {study_plan.get('generated_at', 'Unknown')}\n")
                f.write(f"**Duration:** {study_plan.get('study_duration', 0)} days\n")
                f.write(f"**Hours per Day:** {study_plan.get('hours_per_day', 0)}\n")
                f.write(f"**Difficulty:** {study_plan.get('difficulty', 'Medium')}\n")
                f.write(f"**Study Method:** {study_plan.get('study_method', 'Pomodoro')}\n\n")
                
                # Learning Objectives
                f.write("## Learning Objectives\n\n")
                for i, objective in enumerate(study_plan.get('objectives', []), 1):
                    f.write(f"**{i}.** {objective.get('objective', '')}\n")
                    f.write(f"   - **Category:** {objective.get('category', '')}\n")
                    f.write(f"   - **Difficulty:** {objective.get('difficulty', '')}\n")
                    f.write(f"   - **Timeframe:** {objective.get('timeframe', '')}\n")
                    f.write(f"   - **Success Criteria:** {', '.join(objective.get('success_criteria', []))}\n\n")
                
                # Topic Breakdown
                f.write("## Topic Breakdown\n\n")
                for i, unit in enumerate(study_plan.get('topic_breakdown', []), 1):
                    f.write(f"### {i}. {unit.get('title', '')}\n\n")
                    f.write(f"{unit.get('description', '')}\n\n")
                    f.write(f"**Estimated Hours:** {unit.get('estimated_hours', 0)}\n")
                    f.write(f"**Difficulty:** {unit.get('difficulty', '')}\n")
                    f.write(f"**Key Concepts:** {', '.join(unit.get('key_concepts', []))}\n")
                    f.write(f"**Activities:** {', '.join(unit.get('activities', []))}\n\n")
                
                # Study Schedule
                f.write("## Study Schedule\n\n")
                schedule = study_plan.get('schedule', {})
                f.write(f"**Total Hours:** {schedule.get('total_hours', 0)}\n")
                f.write(f"**Study Method:** {schedule.get('study_method', '')}\n\n")
                
                for daily in schedule.get('daily_schedules', []):
                    f.write(f"### Day {daily.get('day', '')} - {daily.get('day_of_week', '')} ({daily.get('date', '')})\n\n")
                    f.write(f"**Total Hours:** {daily.get('total_hours', 0)}\n\n")
                    
                    for session in daily.get('sessions', []):
                        f.write(f"**{session.get('unit', '')}** ({session.get('duration', 0)} hours)\n")
                        f.write(f"- Activities: {', '.join(session.get('activities', []))}\n")
                        f.write(f"- Key Concepts: {', '.join(session.get('key_concepts', []))}\n")
                        f.write(f"- Difficulty: {session.get('difficulty', '')}\n\n")
                
                # Study Tips
                f.write("## Study Tips\n\n")
                for tip in study_plan.get('study_tips', []):
                    f.write(f"- {tip}\n")
                f.write("\n")
                
                # Resources
                f.write("## Study Resources\n\n")
                for resource in study_plan.get('resources', []):
                    f.write(f"### {resource.get('title', '')}\n")
                    f.write(f"**Type:** {resource.get('type', '')}\n")
                    f.write(f"**Description:** {resource.get('description', '')}\n")
                    f.write(f"**Difficulty:** {resource.get('difficulty', '')}\n")
                    if resource.get('url'):
                        f.write(f"**URL:** {resource.get('url', '')}\n")
                    f.write(f"**Cost:** {resource.get('cost', '')}\n")
                    f.write(f"**Recommended:** {'Yes' if resource.get('recommended') else 'No'}\n\n")
                
                # Progress Tracking
                f.write("## Progress Tracking\n\n")
                progress = study_plan.get('progress_tracking', {})
                f.write(f"**Total Units:** {progress.get('total_units', 0)}\n")
                f.write(f"**Total Hours:** {progress.get('total_hours', 0)}\n")
                f.write(f"**Completed Units:** {progress.get('completed_units', 0)}\n")
                f.write(f"**Progress:** {progress.get('progress_percentage', 0):.1f}%\n\n")
                
                f.write("### Milestones\n\n")
                for milestone in progress.get('milestones', []):
                    status = "✅" if milestone.get('completed') else "⏳"
                    f.write(f"{status} **{milestone.get('unit', '')}** (Day {milestone.get('day_target', 0)})\n")
                    if milestone.get('completed'):
                        f.write(f"   Completed: {milestone.get('completion_date', '')}\n")
                    f.write(f"   Notes: {milestone.get('notes', '')}\n\n")
            
            logger.info(f"Study plan exported to Markdown: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export study plan to Markdown: {e}")
            raise 