# 🎬 Master Universal AI Prompt for Video Generation

## 🎯 **What This Is**

This is the **universal AI prompt** that will:
- Take **any topic** with multiple **subtopics**
- Generate **video-ready slides** (one slide per subtopic)
- Each slide has **bullet points** (short text only, no clutter)
- The **narration expands on those points** in detail (not just reading the bullets)
- Slides are **clean, non-overlapping, properly spaced**, with consistent formatting
- **Optimized for video creation** with proper timing and flow

---

## 🔹 **The Master Prompt**

**Copy and paste this prompt into any AI system (ChatGPT, Claude, Gemini, etc.):**

---

```
You are an AI system that generates video slideshows with synced narration in Google NotebookLM style.

## 🎯 TASK
Create a professional VIDEO presentation for: "[YOUR_TOPIC_HERE]"
Audience Level: [beginner/intermediate/advanced]
Target Slides: [NUMBER_OF_SLIDES]
Video Duration: ~[NUMBER_OF_SLIDES * 8] seconds (8 seconds per slide)

## 📋 CRITICAL STYLE RULES - NEVER VIOLATE
- NEVER use question marks (?) anywhere in any content
- NEVER start sentences with "What", "How", "Why", "When", "Where", "Which"
- Write ONLY clear, declarative statements
- Use simple, direct language appropriate for the audience level
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
{
  "topic": "[YOUR_TOPIC]",
  "level": "[beginner/intermediate/advanced]",
  "slides": [
    {
      "title": "clean slide title",
      "subtopics": ["subtopic1", "subtopic2"],
      "bullets": ["bullet1", "bullet2", "bullet3"],
      "narration": "detailed explanation that expands on bullets with context and examples",
      "examples": ["example1", "example2"],
      "visual_prompts": ["visual description 1", "visual description 2"],
      "layout": "suggested animation style",
      "subtopic_type": "definition|comparison|process|advantages_disadvantages|case_study|timeline|classification|principles"
    }
  ]
}

IMPORTANT: 
- Do not include markdown fences or any text outside JSON
- Ensure all text is clean, professional, and free of question marks
- Make narration significantly more detailed than bullet points
- Vary subtopic types to avoid repetition
- Keep slides visually clean and non-overlapping
- Optimize content for video viewing and narration timing
- Ensure smooth flow between slides for video presentation
```

---

## 🚀 **How to Use This Prompt**

### **Step 1: Customize the Prompt**
Replace the placeholders:
- `[YOUR_TOPIC_HERE]` → Your actual topic (e.g., "Machine Learning Basics")
- `[beginner/intermediate/advanced]` → Your audience level
- `[NUMBER_OF_SLIDES]` → How many slides you want (e.g., 6)

### **Step 2: Use with Any AI System**
- **ChatGPT**: Paste the prompt and get JSON output
- **Claude**: Paste the prompt and get JSON output  
- **Gemini**: Paste the prompt and get JSON output
- **Any other AI**: Works with any system that can generate structured content

### **Step 3: Get Your Content**
The AI will return structured JSON with:
- ✅ Clean slide titles
- ✅ Bullet points (short text only)
- ✅ Detailed narration (expands on bullets)
- ✅ Examples and visual prompts
- ✅ Layout suggestions
- ✅ Varied subtopic types

---

## 📝 **Example Usage**

### **Input Prompt (customized):**
```
You are an AI system that generates video slideshows with synced narration in Google NotebookLM style.

## 🎯 TASK
Create a professional presentation for: "Artificial Intelligence Basics"
Audience Level: beginner
Target Slides: 6

[rest of the prompt...]
```

### **Output (JSON):**
```json
{
  "topic": "Artificial Intelligence Basics",
  "level": "beginner",
  "slides": [
    {
      "title": "What is AI",
      "subtopics": ["Definition", "Core Concepts"],
      "bullets": [
        "Machines simulating human intelligence",
        "Learning and adapting capabilities",
        "Decision-making without human input"
      ],
      "narration": "Artificial Intelligence refers to the ability of machines to perform tasks that normally require human intelligence. This includes learning from data, adapting to new situations, and making decisions without explicit instructions. AI systems can process vast amounts of information and identify patterns that humans might miss.",
      "examples": [
        "Voice assistants like Siri and Alexa",
        "Recommendation systems on Netflix"
      ],
      "visual_prompts": [
        "Brain and computer chip connected by neural network lines",
        "Simple flowchart showing input → processing → output"
      ],
      "layout": "clean minimal, bullets fade in one by one",
      "subtopic_type": "definition"
    }
  ]
}
```

---

## 🎭 **Subtopic Types Explained**

The prompt automatically uses **8 different subtopic types** to create variety:

1. **Definition** - Clear explanations (fade-in animations)
2. **Comparison** - Side-by-side contrasts (alternating reveals)
3. **Process** - Step-by-step workflows (timeline style)
4. **Advantages/Disadvantages** - Pros and cons (two-column grid)
5. **Case Study** - Real-world examples (storyboard style)
6. **Timeline** - Historical development (chronological reveal)
7. **Classification** - Categorization systems (hierarchical tree)
8. **Principles** - Core concepts (card-based grid)

---

## 🎯 **Perfect For**

- ✅ **Content creators** who need professional slides
- ✅ **Educators** creating lesson materials
- ✅ **Business presenters** needing structured content
- ✅ **Video creators** who want slide-to-video content
- ✅ **Anyone** who needs NotebookLM-style presentations

---

## 🎉 **Benefits**

- 🎬 **Universal** - Works with any topic
- 🎨 **Professional** - NotebookLM-style quality
- 🧹 **Clean** - No question marks, proper formatting
- 🎭 **Varied** - 8 different content types
- 📊 **Structured** - Consistent JSON output
- 🚀 **Ready-to-use** - No coding required

---

**That's it!** This is the **master universal AI prompt** that will generate professional, NotebookLM-style slide content for any topic. Just customize the placeholders and use it with any AI system! 🎬✨ 