import structlog
import re
import time
from ..core.a2a import A2AProtocol
from ..core.session_service import SessionService
from ..core.memory_bank import MemoryBank
from ..core.llm_service import get_llm_service
from ..tools.calendar_tool import CalendarTool
from ..tools.web_search_tool import WebSearchTool
from ..tools.shopping_tool import ShoppingTool
from typing import Dict, Any
from .planner import PlannerAgent
from .executor import ExecutorAgent
from .knowledge import KnowledgeAgent
from .memory import MemoryAgent
from .analyzer import AnalyzerAgent

logger = structlog.get_logger()

class RouterAgent:
    def __init__(self):
        logger.info("RouterAgent initialized")
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.knowledge = KnowledgeAgent()
        self.memory = MemoryAgent()
        self.analyzer = AnalyzerAgent()
        
        # Core services
        self.session_service = SessionService()
        self.llm_service = get_llm_service()
        self.memory_bank = MemoryBank()
        
        # Tools
        self.calendar_tool = CalendarTool()
        self.web_search_tool = WebSearchTool()
        self.shopping_tool = ShoppingTool()
    
    def _detect_message_type(self, message: str) -> str:
        """Detect the type of message based on content"""
        message_lower = message.lower()
        
        # Memory storage patterns
        memory_patterns = [
            r'remember\s+that\s+i',
            r'remember\s*:\s*',
            r'i\s+have\s+a\s+(meeting|appointment|deadline|task)',
            r'my\s+(preference|habit|routine)',
            r'i\s+(prefer|like|enjoy|want|need)',
            r'store\s+this',
            r'keep\s+in\s+mind'
        ]
        
        # Memory retrieval patterns
        retrieval_patterns = [
            r'what\s+(do\s+you\s+know|can\s+you\s+tell\s+me)',
            r'what\s+(have\s+i\s+told|did\s+i\s+say)',
            r'remember\s+that\s+i',
            r'what\s+(about|regarding)',
            r'tell\s+me\s+about\s+my',
            r'what\s+(meetings|deadlines|tasks|preferences)',
            r'do\s+you\s+remember'
        ]
        
        # Knowledge query patterns
        knowledge_patterns = [
            r'what\s+(are|is)',
            r'how\s+(do|does|to)',
            r'why\s+(is|are|do)',
            r'explain\s+',
            r'describe\s+',
            r'(search|find|look\s+up)',
            r'information\s+about',
            r'best\s+practices',
            r'(latest|recent)',
            r'trends\s+in'
        ]
        
        # Planning patterns
        planning_patterns = [
            r'plan\s+(my|for\s+me)',
            r'help\s+me\s+plan',
            r'create\s+a\s+plan',
            r'(schedule|organize)',
            r'project\s+plan',
            r'daily\s+plan',
            r'weekly\s+plan',
            r'how\s+should\s+i',
            r'what\s+should\s+i',
            r'plan\s+my\s+(day|week|month)',
            r'organize\s+my',
            r'schedule\s+my',
            r'help\s+me\s+organize',
            r'create\s+a\s+schedule',
            r'make\s+a\s+plan',
            r'prepare\s+a\s+plan',
            r'plan\s+out',
            r'plan\s+to',
            r'strategy\s+for',
            r'roadmap\s+for',
            r'steps\s+to',
            r'how\s+to\s+(start|begin|organize|plan)',
            r'what\s+are\s+the\s+steps',
            r'break\s+down\s+(this|it)',
            r'outline\s+for'
        ]
        
        # Context continuation patterns
        context_patterns = [
            r'continue',
            r'next',
            r'go\s+on',
            r'tell\s+me\s+more',
            r'what\s+else',
            r'and\s+then',
            r'after\s+that',
            r'following\s+up',
            r'let\'s\s+continue',
            r'carry\s+on',
            r'proceed',
            r'more\s+details',
            r'elaborate',
            r'expand\s+on',
            r'further\s+information'
        ]
        
        # Error handling patterns
        error_patterns = [
            r'error',
            r'bug',
            r'issue',
            r'problem',
            r'not\s+working',
            r'failed',
            r'exception',
            r'stack\s+trace',
            r'debug',
            r'troubleshoot',
            r'fix\s+(this|it)',
            r'broken',
            r'crash',
            r'mistake',
            r'wrong',
            r'incorrect',
            r'help\s+me\s+fix'
        ]
        
        # Check patterns in priority order
        for pattern in memory_patterns:
            if re.search(pattern, message_lower):
                return "memory_store"
                
        for pattern in retrieval_patterns:
            if re.search(pattern, message_lower):
                return "memory_retrieve"
                
        for pattern in knowledge_patterns:
            if re.search(pattern, message_lower):
                return "knowledge_search"
                
        for pattern in planning_patterns:
            if re.search(pattern, message_lower):
                return "planning_request"
                
        for pattern in context_patterns:
            if re.search(pattern, message_lower):
                return "context_continuation"
                
        for pattern in error_patterns:
            if re.search(pattern, message_lower):
                return "error_handling"
        
        # Default to general conversation (will be handled by real Gemini, not mock)
        return "general"

    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process message through intelligent routing"""
        import time
        start_time = time.time()
        
        logger.info("Processing message", user_id=user_id, message=message)
        
        # Create or get session
        session_id = self.session_service.create_session(user_id)
        session = self.session_service.get_session(session_id)
        
        # Store the user message in memory bank
        self.memory_bank.store_memory(user_id, "last_message", message, "chat")
        self.session_service.increment_message_count(session_id)
        
        # Detect message type and route accordingly
        message_type = self._detect_message_type(message)
        logger.info("Message type detected", type=message_type, message=message, user_id=user_id)
        
        agent_used = None
        tools_used = []
        final_response = ""
        
        try:
            if message_type == "memory_store":
                logger.info("Processing memory storage", user_id=user_id)
                agent_used = "memory_agent"
                tools_used = ["memory_bank", "vector_store"]
                # Handle memory storage - extract key and value from message
                # For now, store the full message as a memory
                memory_key = f"memory_{int(time.time())}"
                memory_response = await self.memory.store_memory(user_id, memory_key, message, "user_stored")
                final_response = memory_response.payload.get("response", "Memory stored successfully.")
                logger.info("Memory storage completed", user_id=user_id, memory_key=memory_key)
                
            elif message_type == "memory_retrieve":
                logger.info("Processing memory retrieval", user_id=user_id)
                agent_used = "memory_agent"
                tools_used = ["memory_bank", "vector_search"]
                # Handle memory retrieval - search for relevant memories
                retrieval_response = await self.memory.search_similar_memories(user_id, message, k=5)
                memories = retrieval_response.payload.get("memory_value", [])
                summary = retrieval_response.payload.get("summary", "")
                
                if memories:
                    if summary:
                        final_response = f"{summary}\n\nRelevant memories:\n{chr(10).join(memories)}"
                    else:
                        final_response = f"Found relevant memories:\n{chr(10).join(memories)}"
                    logger.info("Memory retrieval completed", user_id=user_id, memories_count=len(memories))
                else:
                    final_response = "I don't have any relevant memories about that."
                    logger.info("No relevant memories found", user_id=user_id)
                    
            elif message_type == "knowledge_search":
                logger.info("Processing knowledge search", user_id=user_id)
                agent_used = "knowledge_agent"
                tools_used = ["web_search", "knowledge_base"]
                # Handle knowledge queries - use web search tool
                search_results = await self.knowledge.search_knowledge(message, user_id, self.web_search_tool)
                knowledge_data = search_results.payload.get("results", [])
                
                if knowledge_data:
                    # Format knowledge results for display
                    formatted_results = []
                    for item in knowledge_data:
                        if isinstance(item, dict):
                            formatted_results.append(f"- {item.get('title', 'Untitled')}: {item.get('snippet', 'No description')}")
                        else:
                            formatted_results.append(str(item))
                    
                    final_response = f"Here's what I found:\n\n{chr(10).join(formatted_results)}"
                    logger.info("Knowledge search completed", user_id=user_id, results_count=len(knowledge_data))
                else:
                    final_response = "I couldn't find relevant information for your query."
                    logger.info("No knowledge results found", user_id=user_id)
                    
            elif message_type == "planning_request":
                logger.info("Processing planning request", user_id=user_id)
                agent_used = "planning_agent"
                tools_used = ["task_planner", "llm_service"]
                # Handle planning requests
                plan_response = await self.planner.create_plan(message, user_id)
                plan_steps = plan_response.payload.get("steps", [])
                
                if plan_steps:
                    final_response = f"Here's your plan:\n\n{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(plan_steps))}"
                    logger.info("Planning completed", user_id=user_id, steps_count=len(plan_steps))
                else:
                    final_response = "I couldn't create a plan for that request."
                    logger.info("Planning failed", user_id=user_id)
                    
            elif message_type == "context_continuation":
                logger.info("Processing context continuation", user_id=user_id)
                agent_used = "conversation_agent"
                tools_used = ["llm_service"]
                # Handle context continuation with real Gemini
                final_response = self.llm_service.generate_text(
                    f"Continue the conversation naturally based on the user's message: {message}"
                )
                logger.info("Context continuation completed", user_id=user_id)
                
            elif message_type == "error_handling":
                logger.info("Processing error handling", user_id=user_id)
                agent_used = "debugging_agent"
                tools_used = ["llm_service", "error_analyzer"]
                # Handle error messages with real Gemini
                final_response = self.llm_service.generate_text(
                    f"Analyze this error or issue and provide real debugging help: {message}"
                )
                logger.info("Error handling completed", user_id=user_id)
                
            else:
                logger.info("Processing general conversation", user_id=user_id)
                agent_used = "conversation_agent"
                tools_used = ["llm_service"]
                # Default: Use real Gemini for general conversation (NO MORE MOCK PIPELINE)
                final_response = self.llm_service.generate_text(message)
                logger.info("General conversation completed", user_id=user_id)
            
            # Store final response in session context
            self.session_service.update_session_context(session_id, "last_response", final_response)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            logger.info("Message processed successfully", user_id=user_id, session_id=session_id, message_type=message_type)
            
            return {
                "response": final_response,
                "agent_used": agent_used,
                "tools_used": tools_used,
                "processing_time": processing_time,
                "message_type": message_type
            }
            
        except Exception as e:
            logger.error("Error processing message", user_id=user_id, message_type=message_type, error=str(e))
            # Fallback to basic response
            final_response = "I apologize, but I encountered an error processing your request. Please try again."
            logger.info("Fallback response used", user_id=user_id)
            
            return {
                "response": final_response,
                "agent_used": "error_handler",
                "tools_used": ["error_recovery"],
                "processing_time": time.time() - start_time,
                "message_type": "error"
            }