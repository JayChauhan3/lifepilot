# Analyzer Agent
import structlog
from app.schemas import AgentMessage
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..core.llm_service import get_llm_service
from ..core.memory_bank import get_memory_bank

logger = structlog.get_logger()

class AnalyzerAgent:
    def __init__(self):
        logger.info("AnalyzerAgent initialized")
        self.llm_service = get_llm_service()
        self.memory_bank = get_memory_bank()
    
    async def analyze_intent(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user intent and route message to appropriate subsystem.
        Returns ONLY JSON with route information.
        """
        logger.info("Analyzing intent", message=message)
        
        # Reuse the existing routing logic but wrapped in a cleaner method name
        # This is called by Orchestrator
        
        message_lower = message.lower()
        
        # Memory storage patterns
        if any(pattern in message_lower for pattern in [
            'remember', 'store this', 'keep in mind', 'i have a', 'my preference', 
            'i prefer', 'i like', 'i enjoy', 'i want', 'i need'
        ]):
            return {"route": "memory_store"}
        
        # Memory retrieval patterns  
        if any(pattern in message_lower for pattern in [
            'what do you know', 'what can you tell me', 'what have i told', 'did i say',
            'remember that i', 'what about', 'regarding', 'tell me about my'
        ]):
            return {"route": "memory_recall"}
        
        # Knowledge search patterns
        if any(pattern in message_lower for pattern in [
            'what are', 'how do', 'why is', 'explain', 'describe', 'search', 'find',
            'look up', 'information about', 'best practices', 'latest', 'recent', 'trends'
        ]):
            return {"route": "knowledge_search"}
        
        # Planning patterns
        if any(pattern in message_lower for pattern in [
            'plan', 'schedule', 'organize', 'help me plan', 'create a plan',
            'how should i', 'what should i', 'strategy for', 'steps to'
        ]):
            return {"route": "plan_generation"}
        
        # Context continuation patterns
        if any(pattern in message_lower for pattern in [
            'continue', 'next', 'go on', 'tell me more', 'what else', 'and then',
            'after that', 'following up', 'proceed', 'elaborate', 'expand on'
        ]):
            return {"route": "context_continuation"}
        
        # Error handling patterns
        if any(pattern in message_lower for pattern in [
            'error', 'bug', 'issue', 'problem', 'not working', 'failed', 'exception',
            'stack trace', 'debug', 'troubleshoot', 'fix', 'broken', 'crash'
        ]):
            return {"route": "error_analysis"}
            
        # Analysis patterns (NEW)
        if any(pattern in message_lower for pattern in [
            'analyze', 'analysis', 'summary', 'report', 'productivity', 'stats', 'how did i do'
        ]):
            return {"route": "analysis"}
        
        # Default to general chat
        return {"route": "default_chat"}

    # Alias for backward compatibility if needed
    async def route_message(self, message: str) -> str:
        import json
        result = await self.analyze_intent(message)
        return json.dumps(result)

    async def analyze_productivity(self, user_id: str, period: str = "week") -> Dict[str, Any]:
        """Analyze productivity based on completed tasks and logs"""
        logger.info("Analyzing productivity", user_id=user_id, period=period)
        
        # In a real implementation, we would fetch completed tasks from a database
        # For now, we'll simulate fetching from memory/logs or return a mock analysis
        
        # Mock data for demonstration
        completed_tasks = 12
        total_tasks = 15
        productivity_score = 80
        
        analysis = {
            "period": period,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "productivity_score": productivity_score,
            "insights": [
                "Most productive time: Morning (9 AM - 11 AM)",
                "Most frequent task type: Coding",
                "Suggestion: Take more breaks in the afternoon"
            ]
        }
        
        # Use LLM to generate a natural language summary of the stats
        summary_prompt = f"Generate a productivity summary for a user who completed {completed_tasks}/{total_tasks} tasks this {period}. Score: {productivity_score}%. Insights: {analysis['insights']}"
        
        try:
            natural_summary = self.llm_service.generate_text(summary_prompt, max_tokens=200)
            analysis["summary"] = natural_summary
        except Exception as e:
            logger.error("Failed to generate productivity summary", error=str(e))
            analysis["summary"] = "Productivity analysis completed."
            
        return analysis

    async def generate_weekly_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate a weekly summary of activities"""
        logger.info("Generating weekly summary", user_id=user_id)
        
        # Reuse analyze_productivity for now
        return await self.analyze_productivity(user_id, period="week")

    async def process_task(self, task: str, context: Dict[str, Any] = None) -> AgentMessage:
        """Process a generic analysis task"""
        logger.info("Processing analysis task", task=task)
        
        # Use LLM to perform the analysis task
        try:
            response = self.llm_service.generate_text(
                f"Perform the following analysis task: {task}. Provide a concise summary of your findings.",
                max_tokens=500
            )
            result = response
            status = "completed"
        except Exception as e:
            logger.error("Failed to process analysis task", error=str(e))
            result = f"Failed to process task: {str(e)}"
            status = "failed"
            
        return AgentMessage(
            sender="analyzer",
            receiver="orchestrator",
            type="ANALYSIS_RESULT",
            payload={
                "task": task,
                "result": result,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        )