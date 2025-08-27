import json
import tempfile
import os
from typing import Dict, List, Any, Optional
import logging
from config import Config
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MindMapGenerator:
    """Generates visual mind maps from topics and concepts using Gemini AI"""
    
    def __init__(self):
        self.config = Config()
        self.default_width = 1920
        self.default_height = 1080
        self.node_colors = [
            (52, 152, 219),   # Blue
            (46, 204, 113),   # Green
            (155, 89, 182),   # Purple
            (230, 126, 34),   # Orange
            (231, 76, 60),    # Red
            (241, 196, 15),   # Yellow
            (26, 188, 156),   # Teal
            (52, 73, 94)      # Dark Gray
        ]
    
    def generate_mind_map_structure(self, topic: str, ai_service) -> Dict[str, Any]:
        """Generate mind map structure using Gemini AI"""
        try:
            # Enhanced prompt for better AI response
            prompt = f"""
You are an expert educator creating a comprehensive mind map for the topic: "{topic}"

Create a detailed, educational mind map structure that covers:
1. Main topic (central concept)
2. 4-6 primary branches (major themes/concepts)
3. 2-4 sub-branches for each primary branch
4. Key points/details for each sub-branch

Requirements:
- Use clear, educational language
- Focus on learning and understanding
- Include practical applications where relevant
- Ensure logical flow and connections
- Make it comprehensive but not overwhelming

Return ONLY valid JSON with this exact structure:
{{
  "topic": "Main Topic Name",
  "description": "Brief description of the topic",
  "main_branches": [
    {{
      "title": "Primary Branch Title",
      "color": "blue",
      "description": "Brief description of this branch",
      "sub_branches": [
        {{
          "title": "Sub-branch Title",
          "description": "Brief description",
          "key_points": ["Point 1", "Point 2", "Point 3", "Point 4"]
        }}
      ]
    }}
  ]
}}

Color options: blue, green, purple, orange, red, yellow, teal, gray
Ensure the JSON is properly formatted and valid.
"""
            
            # Get AI response
            response = ai_service.generate_response(prompt)
            logger.info(f"AI response received for mind map: {topic}")
            
            # Extract JSON from response
            try:
                # Find JSON in the response
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    data = json.loads(json_str)
                    
                    # Validate structure
                    if self._validate_mind_map_structure(data):
                        logger.info(f"Valid mind map structure generated for: {topic}")
                        return data
                    else:
                        logger.warning(f"Invalid mind map structure, using fallback for: {topic}")
                        return self._create_fallback_mind_map(topic)
                        
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Response was: {response[:200]}...")
                return self._create_fallback_mind_map(topic)
            except Exception as e:
                logger.error(f"Error processing AI response: {e}")
                return self._create_fallback_mind_map(topic)
            
        except Exception as e:
            logger.error(f"Failed to generate mind map structure: {e}")
            return self._create_fallback_mind_map(topic)
    
    def _validate_mind_map_structure(self, data: Dict[str, Any]) -> bool:
        """Validate mind map structure"""
        try:
            required_keys = ["topic", "main_branches"]
            if not all(key in data for key in required_keys):
                return False
            
            if not isinstance(data["main_branches"], list):
                return False
            
            for branch in data["main_branches"]:
                if not isinstance(branch, dict):
                    return False
                if "title" not in branch or "sub_branches" not in branch:
                    return False
                if not isinstance(branch["sub_branches"], list):
                    return False
                
                for sub_branch in branch["sub_branches"]:
                    if not isinstance(sub_branch, dict):
                        return False
                    if "title" not in sub_branch or "key_points" not in sub_branch:
                        return False
                    if not isinstance(sub_branch["key_points"], list):
                        return False
            
            return True
        except:
            return False
    
    def _create_fallback_mind_map(self, topic: str) -> Dict[str, Any]:
        """Create a comprehensive fallback mind map structure"""
        return {
            "topic": topic,
            "description": f"Comprehensive overview of {topic}",
            "main_branches": [
                {
                    "title": "Core Concepts",
                    "color": "blue",
                    "description": "Fundamental principles and basic understanding",
                    "sub_branches": [
                        {
                            "title": "Basic Principles",
                            "description": "Essential foundational concepts",
                            "key_points": ["Fundamental ideas", "Core concepts", "Essential elements", "Basic understanding"]
                        },
                        {
                            "title": "Key Components",
                            "description": "Main parts and elements",
                            "key_points": ["Main parts", "Important elements", "Critical factors", "Primary components"]
                        },
                        {
                            "title": "Definitions",
                            "description": "Important terms and concepts",
                            "key_points": ["Key terminology", "Important definitions", "Core vocabulary", "Essential terms"]
                        }
                    ]
                },
                {
                    "title": "Applications",
                    "color": "green",
                    "description": "Real-world uses and practical applications",
                    "sub_branches": [
                        {
                            "title": "Real-world Uses",
                            "description": "Practical applications in various fields",
                            "key_points": ["Practical applications", "Industry usage", "Everyday examples", "Professional uses"]
                        },
                        {
                            "title": "Benefits",
                            "description": "Advantages and positive outcomes",
                            "key_points": ["Advantages", "Positive outcomes", "Value creation", "Benefits"]
                        },
                        {
                            "title": "Case Studies",
                            "description": "Real examples and success stories",
                            "key_points": ["Success stories", "Real examples", "Case studies", "Practical demonstrations"]
                        }
                    ]
                },
                {
                    "title": "Process & Methods",
                    "color": "purple",
                    "description": "Step-by-step processes and methodologies",
                    "sub_branches": [
                        {
                            "title": "Step-by-step Process",
                            "description": "Detailed methodology and procedures",
                            "key_points": ["Step-by-step process", "Methodology", "Procedures", "Systematic approach"]
                        },
                        {
                            "title": "Best Practices",
                            "description": "Recommended approaches and strategies",
                            "key_points": ["Recommended approaches", "Effective methods", "Success strategies", "Best practices"]
                        },
                        {
                            "title": "Tools & Resources",
                            "description": "Required tools and helpful resources",
                            "key_points": ["Required tools", "Helpful resources", "Supporting materials", "Essential equipment"]
                        }
                    ]
                },
                {
                    "title": "Advanced Topics",
                    "color": "orange",
                    "description": "Complex concepts and advanced understanding",
                    "sub_branches": [
                        {
                            "title": "Complex Concepts",
                            "description": "Advanced and sophisticated ideas",
                            "key_points": ["Advanced ideas", "Sophisticated concepts", "Deep understanding", "Complex theories"]
                        },
                        {
                            "title": "Future Trends",
                            "description": "Emerging developments and future directions",
                            "key_points": ["Emerging developments", "Future directions", "Innovation areas", "Trending topics"]
                        },
                        {
                            "title": "Research Areas",
                            "description": "Current research and development",
                            "key_points": ["Current research", "Development areas", "Innovation opportunities", "Research frontiers"]
                        }
                    ]
                },
                {
                    "title": "Challenges & Solutions",
                    "color": "red",
                    "description": "Common challenges and their solutions",
                    "sub_branches": [
                        {
                            "title": "Common Challenges",
                            "description": "Frequently encountered problems",
                            "key_points": ["Common problems", "Frequent challenges", "Typical issues", "Obstacles"]
                        },
                        {
                            "title": "Solutions",
                            "description": "Effective solutions and workarounds",
                            "key_points": ["Effective solutions", "Workarounds", "Problem-solving", "Remedies"]
                        },
                        {
                            "title": "Prevention",
                            "description": "Preventive measures and strategies",
                            "key_points": ["Preventive measures", "Risk mitigation", "Proactive strategies", "Avoidance techniques"]
                        }
                    ]
                }
            ]
        }
    
    def create_mind_map_image(self, mind_map_data: Dict[str, Any], output_path: str = None) -> str:
        """Create a visual mind map image with enhanced design"""
        try:
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                output_path = temp_file.name
                temp_file.close()
            
            # Create image with better resolution
            img = Image.new('RGB', (self.default_width, self.default_height), (248, 249, 250))
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts, fallback to default if not available
            try:
                font_large = ImageFont.truetype("arial.ttf", 40)
                font_medium = ImageFont.truetype("arial.ttf", 28)
                font_small = ImageFont.truetype("arial.ttf", 20)
                font_tiny = ImageFont.truetype("arial.ttf", 16)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
                font_tiny = ImageFont.load_default()
            
            # Draw central topic
            center_x, center_y = self.default_width // 2, self.default_height // 2
            topic = mind_map_data.get("topic", "Topic")
            description = mind_map_data.get("description", "")
            
            # Draw central circle with gradient effect
            circle_radius = 100
            draw.ellipse([
                center_x - circle_radius, center_y - circle_radius,
                center_x + circle_radius, center_y + circle_radius
            ], fill=(52, 152, 219), outline=(44, 62, 80), width=4)
            
            # Draw topic text
            bbox = draw.textbbox((0, 0), topic, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text(
                (center_x - text_width // 2, center_y - text_height // 2),
                topic, fill=(255, 255, 255), font=font_large
            )
            
            # Draw description if available
            if description:
                bbox = draw.textbbox((0, 0), description, font=font_tiny)
                desc_width = bbox[2] - bbox[0]
                draw.text(
                    (center_x - desc_width // 2, center_y + circle_radius + 10),
                    description, fill=(100, 100, 100), font=font_tiny
                )
            
            # Draw main branches
            main_branches = mind_map_data.get("main_branches", [])
            num_branches = len(main_branches)
            
            for i, branch in enumerate(main_branches):
                # Calculate position
                angle = (2 * math.pi * i) / num_branches
                distance = 350
                branch_x = center_x + int(distance * math.cos(angle))
                branch_y = center_y + int(distance * math.sin(angle))
                
                # Get color
                color_name = branch.get("color", "blue")
                color = self._get_color_from_name(color_name)
                
                # Draw branch circle
                branch_radius = 70
                draw.ellipse([
                    branch_x - branch_radius, branch_y - branch_radius,
                    branch_x + branch_radius, branch_y + branch_radius
                ], fill=color, outline=(44, 62, 80), width=3)
                
                # Draw branch title
                title = branch.get("title", "Branch")
                bbox = draw.textbbox((0, 0), title, font=font_medium)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text(
                    (branch_x - text_width // 2, branch_y - text_height // 2),
                    title, fill=(255, 255, 255), font=font_medium
                )
                
                # Draw connection line with arrow effect
                self._draw_connection_line(draw, center_x, center_y, branch_x, branch_y, color)
                
                # Draw sub-branches
                sub_branches = branch.get("sub_branches", [])
                for j, sub_branch in enumerate(sub_branches):
                    sub_angle = angle + (j - len(sub_branches) // 2) * 0.4
                    sub_distance = 180
                    sub_x = branch_x + int(sub_distance * math.cos(sub_angle))
                    sub_y = branch_y + int(sub_distance * math.sin(sub_angle))
                    
                    # Draw sub-branch rectangle
                    sub_title = sub_branch.get("title", "Sub-branch")
                    sub_desc = sub_branch.get("description", "")
                    key_points = sub_branch.get("key_points", [])
                    
                    # Calculate text dimensions
                    bbox = draw.textbbox((0, 0), sub_title, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Add space for key points
                    points_height = len(key_points) * 20 if key_points else 0
                    rect_width = max(text_width + 30, 200)
                    rect_height = text_height + points_height + 20
                    
                    # Draw rectangle with rounded corners effect
                    draw.rectangle([
                        sub_x - rect_width // 2, sub_y - rect_height // 2,
                        sub_x + rect_width // 2, sub_y + rect_height // 2
                    ], fill=(255, 255, 255), outline=color, width=2)
                    
                    # Draw sub-branch title
                    draw.text(
                        (sub_x - text_width // 2, sub_y - rect_height // 2 + 5),
                        sub_title, fill=(50, 50, 50), font=font_small
                    )
                    
                    # Draw key points
                    y_offset = sub_y - rect_height // 2 + text_height + 10
                    for k, point in enumerate(key_points[:3]):  # Limit to 3 points for space
                        point_text = f"• {point}"
                        bbox = draw.textbbox((0, 0), point_text, font=font_tiny)
                        point_width = bbox[2] - bbox[0]
                        draw.text(
                            (sub_x - point_width // 2, y_offset + k * 18),
                            point_text, fill=(80, 80, 80), font=font_tiny
                        )
                    
                    # Draw connection line
                    draw.line([(branch_x, branch_y), (sub_x, sub_y)], 
                             fill=(150, 150, 150), width=2)
            
            # Save image
            img.save(output_path, "PNG", quality=95)
            logger.info(f"Mind map image created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create mind map image: {e}")
            raise
    
    def _draw_connection_line(self, draw, x1, y1, x2, y2, color):
        """Draw connection line with arrow effect"""
        # Main line
        draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 100), width=3)
        
        # Arrow head
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_length = 15
        arrow_angle = math.pi / 6
        
        # Arrow points
        arrow_x1 = x2 - arrow_length * math.cos(angle - arrow_angle)
        arrow_y1 = y2 - arrow_length * math.sin(angle - arrow_angle)
        arrow_x2 = x2 - arrow_length * math.cos(angle + arrow_angle)
        arrow_y2 = y2 - arrow_length * math.sin(angle + arrow_angle)
        
        draw.line([(x2, y2), (arrow_x1, arrow_y1)], fill=color, width=2)
        draw.line([(x2, y2), (arrow_x2, arrow_y2)], fill=color, width=2)
    
    def _get_color_from_name(self, color_name: str) -> tuple:
        """Convert color name to RGB tuple"""
        color_map = {
            "blue": (52, 152, 219),
            "green": (46, 204, 113),
            "purple": (155, 89, 182),
            "orange": (230, 126, 34),
            "red": (231, 76, 60),
            "yellow": (241, 196, 15),
            "teal": (26, 188, 156),
            "gray": (52, 73, 94)
        }
        return color_map.get(color_name.lower(), (52, 152, 219))
    
    def generate_mind_map_video(self, topic: str, ai_service, output_path: str = None) -> str:
        """Generate a video showing mind map creation with narration"""
        try:
            # Generate mind map structure using AI
            mind_map_data = self.generate_mind_map_structure(topic, ai_service)
            
            # Create mind map image
            image_path = self.create_mind_map_image(mind_map_data)
            
            # Convert to video with narration
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                output_path = temp_file.name
                temp_file.close()
            
            # Create narration text using AI
            narration_prompt = f"""
Create a clear, educational narration for a mind map video about "{topic}".

The mind map has these main branches:
{chr(10).join([f"- {branch.get('title', 'Branch')}: {branch.get('description', '')}" for branch in mind_map_data.get('main_branches', [])])}

Create a 30-45 second narration that:
1. Introduces the topic
2. Explains the main branches and their importance
3. Highlights key insights
4. Concludes with a summary

Use clear, engaging language suitable for educational content.
Keep it concise but informative.
"""
            
            narration = ai_service.generate_response(narration_prompt)
            
            # Fallback narration if AI fails
            if not narration or len(narration) < 50:
                narration = f"Welcome to this mind map about {topic}. This visual representation shows the main concepts and their relationships. "
                narration += f"The central topic is {topic}. "
                
                for i, branch in enumerate(mind_map_data.get("main_branches", [])):
                    narration += f"The {i+1} main branch covers {branch.get('title', 'concepts')}. "
                    for sub_branch in branch.get("sub_branches", []):
                        narration += f"This includes {sub_branch.get('title', 'elements')}. "
                
                narration += f"This mind map provides a comprehensive overview of {topic} and its key components."
            
            # Generate video using video generator
            from video_generator import VideoGenerator
            video_gen = VideoGenerator()
            
            video_path = video_gen.generate_video(
                text=narration,
                duration=45,
                output_path=output_path,
                topic=topic
            )
            
            # Cleanup
            if os.path.exists(image_path):
                os.unlink(image_path)
            
            logger.info(f"Mind map video generated: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Failed to generate mind map video: {e}")
            raise 