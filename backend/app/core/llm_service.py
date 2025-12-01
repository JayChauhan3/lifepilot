# LLM Service for Gemini integration
import structlog
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
import google.generativeai as genai

logger = structlog.get_logger()

class LLMProvider:
    """Base class for LLM providers"""
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text from prompt"""
        raise NotImplementedError

class GeminiLLM(LLMProvider):
    """Google Gemini LLM using API key authentication"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        self.model_name = model_name
        self._model = None
        self._initialized = False
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini with API key"""
        if self._initialized:
            return
            
        from app.config import settings
        api_key = settings.GEMINI_API_KEY
            
        if not api_key:
            logger.warning("GEMINI_API_KEY not set, using mock responses")
            self._model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self.model_name)
            self._initialized = True
            masked_key = f"{api_key[:4]}...{api_key[-4:]}" if api_key and len(api_key) > 8 else "INVALID"
            logger.info("Gemini initialized with API key", model=self.model_name, key_preview=masked_key)
        except Exception as e:
            logger.error("Failed to initialize Gemini", error=str(e))
            self._model = None
    
    def generate_text(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Generate text using Gemini"""
        logger.info("GeminiLLM generate_text called", model_set=self._model is not None)
        if not self._model:
            # Fallback to mock response
            logger.error("Gemini model not initialized - API key missing")
            raise ValueError("Gemini API key not configured. Cannot generate response.")
        
        try:
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            response = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            result = response.text
            logger.info("Gemini response received", response_length=len(result))
            return result
        except Exception as e:
            logger.error("Error generating content with Gemini", error=str(e))
            raise e
    
    def _mock_response(self, prompt: str) -> str:
        """Mock response when Gemini is not available"""
        if "plan" in prompt.lower():
            return """Based on your request, here's a structured plan:

## 📋 Action Plan

| Step | Action | Details |
|------|--------|---------|
| 1 | **Analyze** | Analyze current requirements and constraints |
| 2 | **Breakdown** | Break down the task into manageable subtasks |
| 3 | **Prioritize** | Prioritize tasks based on importance |
| 4 | **Timeline** | Set realistic timelines for each task |
| 5 | **Execute** | Execute tasks in order of priority |

### 🗓️ Timeline
- **Week 1**: Analysis and planning
- **Week 2-3**: Core implementation
- **Week 4**: Testing and refinement

### 🛠️ Resources Needed
- Time allocation: 2-3 hours per week
- Tools and materials as specified
- Regular progress reviews

💡 **Suggestion**: Would you like me to create a detailed daily schedule for Week 1?"""
        
        elif "search" in prompt.lower() or "find" in prompt.lower():
            return """## 🔍 Search Results Summary

Based on the available information, I found several relevant resources:

### 🔑 Key Findings

| Source Type | Finding | Relevance |
|-------------|---------|-----------|
| Primary | Core requirements identified | High |
| Secondary | Best practices and context | Medium |
| Updates | Recent trends and news | Low |

### 📝 Details
- The most effective approach combines **structured planning** with flexibility
- Consider both *short-term needs* and *long-term goals*
- Regular review and adjustment is recommended

💡 **Suggestion**: I can dive deeper into the "Primary" sources if you're interested."""
        
        else:
            return """I understand your request. Based on the context and information available, here's my response:

## 💡 Key Points

- **Understanding**: Your specific needs and requirements
- **Evaluating**: Available options and alternatives
- **Decisions**: Making informed decisions based on evidence
- **Implementation**: Solutions in a structured manner

### 📊 Comparison

| Option | Pros | Cons |
|--------|------|------|
| Option A | Fast, Cheap | Low Quality |
| Option B | High Quality | Expensive |

I recommend proceeding with a systematic approach to achieve the best results.

💡 **Suggestion**: Shall we start with Option A?"""

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing"""
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate mock response"""
        return f"[Mock Response] Generated {max_tokens} tokens with temperature {temperature} for prompt: {prompt[:100]}..."

class LLMService:
    """Main LLM service with provider switching"""
    
    def __init__(self, provider: Optional[str] = None):
        from app.config import settings
        self.provider_name = provider or settings.LLM_PROVIDER
        self._provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the LLM provider"""
        if self.provider_name == "gemini":
            self._provider = GeminiLLM()
        elif self.provider_name == "mock":
            self._provider = MockLLMProvider()
        else:
            logger.error("Unknown LLM provider", provider=self.provider_name)
            raise ValueError(f"Unknown LLM provider: {self.provider_name}")
        
        logger.info("LLM service initialized", provider=self.provider_name)
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using the configured provider"""
        return self._provider.generate_text(prompt, max_tokens, temperature)
    
    def generate_plan(self, user_message: str, context: str = "") -> Dict[str, Any]:
        """Generate a structured plan"""
        system_prompt = """You are a helpful AI assistant that creates structured action plans.
        Break down the user's request into clear, actionable steps.
        
        IMPORTANT: You must respond with ONLY valid JSON. No additional text before or after the JSON.
        
        Format your response exactly like this:
        {
            "title": "Plan title here",
            "description": "Brief description here",
            "steps": [
                {"step": 1, "action": "First action description", "details": "Additional details if needed"},
                {"step": 2, "action": "Second action description", "details": "Additional details if needed"},
                {"step": 3, "action": "Third action description", "details": "Additional details if needed"}
            ],
            "timeline": "Estimated timeline here",
            "resources": ["Resource 1", "Resource 2"]
        }"""
        
        full_prompt = f"{system_prompt}\n\nUser Request: {user_message}\n"
        if context:
            full_prompt += f"\nContext: {context}\n"
        
        full_prompt += "\n\nGenerate the plan JSON now:"
        
        response = self.generate_text(full_prompt, max_tokens=4000)
        logger.info("Raw Gemini response for plan", response=response[:500])
        
        # Extract JSON using regex
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response

        try:
            # Try to parse JSON response
            plan = json.loads(json_str)
            return plan
        except Exception as e:
            # Fallback to structured format
            logger.warning("Failed to parse JSON from Gemini", error=str(e))
            # Fallback to structured format
            return {
                "title": "Action Plan",
                "description": "Plan based on user request",
                "steps": [
                    {"step": 1, "action": "Analyze requirements", "details": "Analyze the user's request in detail."},
                    {"step": 2, "action": "Create detailed plan", "details": "Break down the task into actionable steps."},
                    {"step": 3, "action": "Execute plan", "details": "Follow the steps to achieve the goal."}
                ],
                "timeline": "As needed",
                "resources": ["Time", "Effort"]
            }
    
    def generate_planner_response(self, user_message: str, context: str = "") -> str:
        """Generate a structured plan using the LifePilot Planner persona"""
        system_prompt = """AI NAME: LifePilot Planner
ROLE: You are the official planning agent of the LifePilot app.
Your only job: Create structured plans, routines, schedules, and step-by-step programs for any area of life where the user wants improvement.

⸻

🔒 STRICT BEHAVIOR RULES

⚠️ CRITICAL: NEVER create tables with empty columns showing only "-" or "N/A"
If a table column would be empty, either:
  a) Remove that column entirely, OR
  b) Fill it with specific, useful information, OR
  c) Use bullet points/lists instead of a table

	1.	You ONLY generate plans, routines, schedules, programs, diets, meal plans, or structured multi-step guidance.
	•	Never answer single questions.
	•	Never give general explanations.
	•	Never go into unrelated topics.
	•	If the user asks a question outside planning → remind them you ONLY make plans.
	2.	All responses must be structured, formatted, and production-ready.
	•	Use clean headings, bullet points, tables, timelines, and days/weeks structure.
	•	Responses must feel like output from a top-tier company (Google/Notion/Fitbit-level).
	3.	Length must match user intent:
	•	If the user asks for a “1-day plan,” keep it short and sharp.
	•	If they ask for a “monthly plan,” keep it concise and strategic — NOT unnecessarily long.
	•	Never dump huge paragraphs.
	4.	If user does not specify duration
→ Ask them:
“How many days or weeks should I plan for?”
	5.	Tone:
	•	Supportive, professional, direct.
	•	No emojis (unless user likes them).
	•	No slang.

⸻

📜 CONVERSATION CONTEXT

If you receive previous conversation history in the context:
- Use it to understand follow-up questions and requests
- Don't ask for information the user already provided in previous messages
- Reference previous exchanges naturally (e.g., "Based on your 4-week timeline...")
- If the user provides clarification (like "4 weeks"), use it to fulfill their original request

Example:
User: "give me a complete roadmap for DSA"
Assistant: "How many weeks or months should I plan for your DSA roadmap?"
User: "4 weeks, Only main topics"
Assistant: Should create a 4-week DSA roadmap focusing on main topics, NOT ask for duration again

⸻

🎯 WHAT YOU CAN PLAN

You can plan ANYTHING lifestyle-related, including:
	•	Fitness / gym / muscle gain / fat loss
	•	Health / wellness / stress reduction
	•	Productivity / time management
	•	Study plans (DSA, coding, exams)
	•	Skill learning (tech, language, music, etc.)
	•	Focus improvement
	•	Daily, weekly, monthly routines
	•	Meal plans (veg-friendly, dietary preferences)
	•	Habit formation
	•	Spiritual / mental wellbeing
	•	Recreational balance (friends, games, sports, outdoors)

⸻

⸻

⛑️ IF SOMETHING IS UNCLEAR OR AMBIGUOUS

1. Try to INFER the user's intent if possible (e.g., "median" might mean "medium intensity" or "medium budget").
2. If you absolutely cannot create a plan, ask a SPECIFIC clarifying question about what is missing.
3. DO NOT use a generic refusal message if the user has provided a topic and duration.

Example of handling ambiguity:
User: "median diet"
AI: "I'll create a medium-intensity diet plan. Did you mean medium cost or medium calorie? I've assumed medium calorie (maintenance) for now."

⚠️ IMPORTANT: NEVER refuse a request that contains planning keywords (like "plan", "routine", "schedule", "diet", "workout") even if it contains ambiguous words like "median". Just infer the best meaning and proceed.

⛔ WHAT YOU MUST REFUSE
	•	Answering single factual questions (e.g., "Who is the president?")
	•	Chatting or small talk (e.g., "How are you?")
    
    (Note: NEVER refuse a request if it asks for a plan, routine, diet, or schedule. Even if it seems odd, try to create a plan for it.)

If you must refuse a non-planning request (like "tell me a joke"), say:
"I am your LifePilot Planner. I only create routines, schedules, and structured plans. Please ask for a plan."

⸻

🚫 CRITICAL FORMATTING RULE:
Numbers and titles MUST be on the SAME line. Do NOT put line breaks between them.

❌ BAD (DO NOT DO THIS):
1.
**Title**

2.
**Overview**

✅ GOOD (DO THIS):
1. **Title** - Concise + relevant title
2. **Overview** - 1–3 lines describing the purpose.

⸻

📘 RESPONSE FORMAT (MANDATORY)

Each plan must follow this structure:

⸻

1. **Title** - Concise + relevant title
(Do not put the title on a new line after the number)
Example: "1. **2-Day Muscle Gain Routine**"

2. **Overview** - 1–3 lines describing the purpose.

3. **Plan Breakdown** - Choose one structure:
	•	Day-by-day
	•	Week-by-week
	•	Morning/Afternoon/Night
	•	Phases (if multi-week)

4. **Table** (Optional but recommended for clarity)

**IMPORTANT TABLE RULES:**
- If you use a table, EVERY column must have meaningful content
- DO NOT create tables with empty columns (like "Details: -")
- If you can't fill a column with useful info, DON'T include that column
- Good table: | Step | Exercise | Sets x Reps | Rest |
- Bad table: | Step | Action | Details | (where Details is always "-")
- Alternative: Use bullet points or numbered lists instead of tables with empty columns

**EXAMPLES:**

❌ BAD (DO NOT DO THIS):
| Step | Action | Details |
| 1 | Warm-up | - |
| 2 | Exercise | - |

✅ GOOD (DO THIS INSTEAD):
Option 1: Remove empty column
| Step | Action |
| 1 | Warm-up |
| 2 | Exercise |

Option 2: Fill with useful info
| Step | Action | Duration | Notes |
| 1 | Warm-up | 5-10 min | Light cardio |
| 2 | Exercise | 30 min | Focus on form |

Option 3: Use lists
1. **Warm-up** - 5-10 minutes of light cardio
2. **Exercise** - 30 minutes, focus on form

5. Notes & Adjustments

Short bullet list.

⸻

💼 BIG-COMPANY OUTPUT QUALITY GUIDELINES

Follow these internal quality standards:

✔ Consistent formatting
✔ Readable spacing
✔ Zero random advice
✔ Always actionable (user can follow today)
✔ Short but strong takeaway summary
✔ No unnecessary text
✔ NO empty table columns or placeholder content (like "-" or "N/A")
✔ Every piece of information must be meaningful and useful
✔ Adjust plan based on user diet, habits, lifestyle (if they provide)
✔ Avoid extreme routines

⸻

🛠️ TOOL AWARENESS (For Your App Pipeline)

If the system includes tools in future (shopping, health data, etc.):
	•	Select the tool only when necessary.
	•	Otherwise produce a clean direct plan.

⸻

🗣️ ABOUT THE INPUT PANEL
	•	User may speak through 11Labs voice recorder
	•	Or type manually
	•	Always treat speech and typed text the same
	•	Remove transcription noise automatically
(Filler words like “uhh,” background noise, etc.)

⸻


"""
        
        try:
            full_prompt = f"{system_prompt}\n\nUser Request: {user_message}\n"
            if context:
                full_prompt += f"\nContext: {context}\n"
            
            response = self.generate_text(full_prompt, max_tokens=2000)
            
            # Validate response
            if not response or len(response.strip()) < 10:
                raise ValueError("Empty or invalid response from LLM")
            
            logger.info("Planner response generated successfully", response_length=len(response))
            return response
            
        except Exception as e:
            logger.error("Planner response generation failed", error=str(e), user_message=user_message[:100])
            # Return a helpful error message that follows the planner persona
            return """I apologize, but I'm having trouble generating your plan right now.

Please try:
- Rephrasing your request more clearly
- Being specific about duration (e.g., "2 days", "1 week", "1 month")
- Simplifying your request
- Checking your internet connection

If the problem persists, please try again in a moment or contact support."""


    def generate_knowledge_response(self, query: str, context: str = "") -> str:
        """Generate knowledge-based response"""
        system_prompt = """You are a knowledgeable assistant. Use the provided context to answer the user's query accurately.
        If the context doesn't contain the answer, say so and provide general guidance."""
        
        full_prompt = f"{system_prompt}\n\nContext: {context}\n\nQuery: {query}"
        
        return self.generate_text(full_prompt, max_tokens=1000)
    
    def generate_memory_summary(self, memories: List[Dict[str, Any]]) -> str:
        """Generate summary of memories"""
        if not memories:
            return "No memories found."
        
        system_prompt = """Summarize the following memories in a concise and helpful way.
        Focus on key patterns, important information, and actionable insights."""
        
        memory_text = "\n".join([f"- {m.get('content', m.get('value', ''))}" for m in memories])
        full_prompt = f"{system_prompt}\n\nMemories:\n{memory_text}"
        
        return self.generate_text(full_prompt, max_tokens=500)

# Global LLM service instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get global LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

def reset_llm_service():
    """Reset LLM service instance (for testing)"""
    global _llm_service
    _llm_service = None
