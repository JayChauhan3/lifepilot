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
            
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set, using mock responses")
            self._model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self.model_name)
            self._initialized = True
            logger.info("Gemini initialized with API key", model=self.model_name)
        except Exception as e:
            logger.error("Failed to initialize Gemini", error=str(e))
            self._model = None
    
    def generate_text(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Generate text using Gemini"""
        logger.info("GeminiLLM generate_text called", model_set=self._model is not None)
        if not self._model:
            # Fallback to mock response
            logger.warning("Gemini model not initialized, using mock response")
            return self._mock_response(prompt)
        
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
            return self._mock_response(prompt)
    
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
        self.provider_name = provider or os.getenv("LLM_PROVIDER", "mock")
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
