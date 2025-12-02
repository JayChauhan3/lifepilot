import structlog
import re
import time
from ..core.a2a import A2AProtocol
from ..core.session_service import SessionService
from ..core.memory_bank import MemoryBank, get_memory_bank
from ..core.llm_service import get_llm_service
from ..tools.calendar_tool import CalendarTool
from ..tools.web_search_tool import WebSearchTool
from ..tools.web_search_tool import WebSearchTool
from typing import Dict, Any
from .planner import PlannerAgent
from .executor import ExecutorAgent
from .knowledge import KnowledgeAgent
from .memory import MemoryAgent
from .analyzer import AnalyzerAgent
from .ui_agent import UIAgent

logger = structlog.get_logger()

class RouterAgent:
    """
    Intelligent Router for user interactions.
    
    ARCHITECTURE NOTE:
    This agent serves as the "Gatekeeper" or "Entry Point" of the system.
    It uses a combination of Regex Pattern Matching (for speed) and LLM Analysis (for complexity)
    to route requests to the appropriate specialized agent.
    """
    def __init__(self):
        logger.info("RouterAgent initialized")
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.knowledge = KnowledgeAgent()
        self.memory = MemoryAgent()
        self.analyzer = AnalyzerAgent()
        self.ui_agent = UIAgent()
        
        # Core services
        self.session_service = SessionService()
        self.llm_service = get_llm_service()
        self.memory_bank = get_memory_bank()
        
        # Tools
        self.calendar_tool = CalendarTool()
        self.web_search_tool = WebSearchTool()
    
    def _detect_message_type(self, message: str) -> str:
        """
        Detect the type of message based on content.
        
        IMPLEMENTATION DETAIL:
        Uses a priority-based Regex matching system to classify intent into:
        - planning_request (Highest Priority)
        - knowledge_search
        - memory_retrieve
        - memory_store
        - context_continuation
        """
        message_lower = message.lower()
        
        # Memory storage patterns
        memory_patterns = [
            r'remember\s+that\s+i',
            r'remember\s*:\s*',
            r'i\s+have\s+a\s+(meeting|appointment|deadline|task)',
            r'my\s+(preference|habit|routine)',
            # r'i\s+(prefer|like|enjoy|want|need)', # Too aggressive, causes false positives
            r'store\s+this',
            r'keep\s+in\s+mind'
        ]
        
        # Memory retrieval patterns (removed 'remember\s+that\s+i' to avoid conflict with storage)
        retrieval_patterns = [
            r'what\s+(do\s+you\s+know|can\s+you\s+tell\s+me)',
            r'what\s+(have\s+i\s+told|did\s+i\s+say)',
            r'what\s+(about|regarding)',
            r'tell\s+me\s+about\s+my',
            r'what\s+(meetings|deadlines|tasks|preferences)',
            r'do\s+you\s+remember',
            r'show\s+(me\s+)?(my\s+)?(stored\s+)?memor(y|ies)',
            r'list\s+(my\s+)?memor(y|ies)',
            r'what\s+did\s+i\s+store'
        ]
        
        # Knowledge query patterns
        knowledge_patterns = [
            r'search\s+for',
            r'find\s+info\s+on',
            r'look\s+up',
            r'what\s+is\s+the\s+(capital|population|meaning|definition)',
            r'who\s+is\s+(the\s+)?(ceo|president|founder)',
            r'latest\s+news\s+about',
            r'current\s+trends\s+in',
            r'best\s+practices\s+for'
        ]
        
        # Planning patterns
        planning_patterns = [
            r'plan\s+(my|for\s+me|for\s+my)',
            r'give\s+me\s+.*plan',
            r'help\s+me\s+plan',
            r'create\s+.*plan',
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
            r'roadmap',  # Match standalone "roadmap" or "DSA roadmap"
            r'give\s+me\s+a\s+(plan|routine|schedule|roadmap)',
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
        
        # UI patterns
        ui_patterns = [
            r'show\s+(my\s+)?dashboard',
            r'display\s+(my\s+)?dashboard',
            r'open\s+(my\s+)?dashboard',
            r'view\s+(my\s+)?dashboard',
            r'show\s+ui',
            r'show\s+interface'
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
        # IMPORTANT: Check Memory Storage BEFORE Memory Retrieval to avoid conflicts
        
        # 1. Memory Storage (Highest priority for "remember that" pattern)
        for pattern in memory_patterns:
            if re.search(pattern, message_lower):
                return "memory_store"
        
        # 2. Planning (High priority - specific intent)
        for pattern in planning_patterns:
            if re.search(pattern, message_lower):
                return "planning_request"

        # 3. Knowledge Search (Specific intent)
        for pattern in knowledge_patterns:
            if re.search(pattern, message_lower):
                return "knowledge_search"

        # 4. Memory Retrieval (After storage check)
        for pattern in retrieval_patterns:
            if re.search(pattern, message_lower):
                return "memory_retrieve"
                
        # 5. Context Continuation
        for pattern in context_patterns:
            if re.search(pattern, message_lower):
                return "context_continuation"
                
        # 6. UI Requests
        for pattern in ui_patterns:
            if re.search(pattern, message_lower):
                return "ui_request"

        # 7. Error Handling
        for pattern in error_patterns:
            if re.search(pattern, message_lower):
                return "error_handling"
        
        # Default to planning request (AI should always behave as a planner)
        return "planning_request"

    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process message through intelligent routing"""
        import time
        start_time = time.time()
        
        logger.info("Processing message", user_id=user_id, message=message)
        
        # Create or get session
        session_id = self.session_service.get_active_session(user_id)
        session = self.session_service.get_session(session_id)
        
        # Store the user message in memory bank and session history
        self.memory_bank.store_memory(user_id, "last_message", message, "chat")
        self.session_service.increment_message_count(session_id)
        self.session_service.add_message(session_id, "user", message)
        
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
                
                try:
                    # Extract clean data from the message
                    # Remove common prefixes like "Remember that", "Remember:", "Store this:", etc.
                    clean_value = message
                    
                    # Remove "Remember that I" or "Remember that" prefix
                    clean_value = re.sub(r'^remember\s+that\s+i\s+', '', clean_value, flags=re.IGNORECASE)
                    clean_value = re.sub(r'^remember\s+that\s+', '', clean_value, flags=re.IGNORECASE)
                    clean_value = re.sub(r'^remember:\s*', '', clean_value, flags=re.IGNORECASE)
                    clean_value = re.sub(r'^store\s+this:\s*', '', clean_value, flags=re.IGNORECASE)
                    clean_value = re.sub(r'^keep\s+in\s+mind:\s*', '', clean_value, flags=re.IGNORECASE)
                    
                    # Capitalize first letter if needed
                    if clean_value and clean_value[0].islower():
                        clean_value = clean_value[0].upper() + clean_value[1:]
                    
                    # Check for duplicates by searching existing memories
                    logger.info("Checking for duplicate memories", user_id=user_id, value=clean_value)
                    existing_memories = self.memory_bank.get_all_memories(user_id)
                    
                    # Check if exact same memory already exists (case-insensitive comparison)
                    clean_value_lower = clean_value.lower().strip()
                    is_duplicate = False
                    
                    for key, existing_value in existing_memories.items():
                        existing_lower = str(existing_value).lower().strip()
                        # Only check for EXACT match, not substring
                        if clean_value_lower == existing_lower:
                            is_duplicate = True
                            logger.info("Duplicate memory detected", user_id=user_id, existing_key=key, new_value=clean_value)
                            break
                    
                    if is_duplicate:
                        final_response = f"ℹ️ I already remember that you: {clean_value.lower()}. No need to store it again!"
                        logger.info("Skipped duplicate memory storage", user_id=user_id)
                    else:
                        # Store new memory
                        memory_key = f"memory_{int(time.time())}"
                        logger.info("Storing cleaned memory", user_id=user_id, key=memory_key, original=message, cleaned=clean_value)
                        
                        memory_response = await self.memory.store_memory(user_id, memory_key, clean_value, "user_stored")
                        
                        logger.info("Memory agent response received", payload=memory_response.payload)
                        
                        # Check if storage was successful
                        if memory_response.payload.get("action") == "stored":
                            final_response = f"✅ Memory stored successfully! I'll remember that you: {clean_value.lower()}"
                        else:
                            final_response = "❌ Failed to store memory. Please try again."
                        
                        logger.info("Memory storage completed", user_id=user_id, memory_key=memory_key, success=memory_response.payload.get("action") == "stored")
                    
                except Exception as e:
                    logger.error("Error in memory storage", user_id=user_id, error=str(e), error_type=type(e).__name__)
                    import traceback
                    logger.error("Memory storage traceback", traceback=traceback.format_exc())
                    final_response = f"❌ Error storing memory: {str(e)}"
                
            elif message_type == "memory_retrieve":
                logger.info("Processing memory retrieval", user_id=user_id)
                agent_used = "memory_agent"
                tools_used = ["memory_bank", "vector_search"]
                
                try:
                    # Get only user-stored memories to avoid system logs/chat history
                    user_memories_dict = self.memory_bank.get_memories_by_category(user_id, "user_stored")
                    
                    # Clean up and format
                    user_memories = []
                    for key, value in user_memories_dict.items():
                        # Format the memory value
                        memory_text = str(value)
                        # Capitalize first letter
                        if memory_text and memory_text[0].islower():
                            memory_text = memory_text[0].upper() + memory_text[1:]
                        
                        user_memories.append(memory_text)
                    
                    if user_memories:
                        # Simple, clean format like ChatGPT
                        formatted_list = "\n".join([f"• {mem}" for mem in user_memories])
                        final_response = f"**Here's what I remember about you:**\n\n{formatted_list}"
                        
                        logger.info("Memory retrieval completed", user_id=user_id, memories_count=len(user_memories))
                    else:
                        final_response = "I don't have any specific memories stored about you yet. You can ask me to remember things by saying 'Remember that...'."
                        logger.info("No relevant memories found", user_id=user_id)
                        
                except Exception as e:
                    logger.error("Error in memory retrieval", user_id=user_id, error=str(e))
                    final_response = f"❌ Error retrieving memories: {str(e)}"
                    
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
                            title = item.get('title', 'Untitled')
                            snippet = item.get('snippet', 'No description')
                            url = item.get('url', '#')
                            formatted_results.append(f"### 🔍 {title}\n_{snippet}_\n[Source]({url})")
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
                
                # Get plan from PlannerAgent
                plan_response = await self.planner.create_plan(message, user_id)
                
                # NEW: Check for raw_response first (from new strict planner persona)
                if "raw_response" in plan_response.payload and plan_response.payload["raw_response"]:
                    # Use the AI-generated Markdown response directly
                    final_response = plan_response.payload["raw_response"]
                    logger.info("Using raw_response from planner", user_id=user_id)
                else:
                    # Fallback: Format steps manually (backwards compatibility)
                    plan_steps = plan_response.payload.get("steps", [])
                    
                    if plan_steps:
                        # Format the plan nicely with Markdown
                        plan_title = plan_response.payload.get("title", "Here's your plan")
                        plan_desc = plan_response.payload.get("description", "")
                        
                        formatted_response = f"## {plan_title}\n\n"
                        if plan_desc:
                            formatted_response += f"_{plan_desc}_\n\n"
                        
                        for i, step in enumerate(plan_steps, 1):
                            if isinstance(step, dict):
                                action = step.get("action", "")
                                details = step.get("details", "")
                                formatted_response += f"**{i}. {action}**\n"
                                if details:
                                    formatted_response += f"   - {details}\n"
                            else:
                                formatted_response += f"{i}. {step}\n"
                        
                        formatted_response += f"\n**Timeline:** {plan_response.payload.get('estimated_duration', 'N/A')}\n"
                        final_response = formatted_response
                        logger.info("Planning completed with fallback formatting", user_id=user_id, steps_count=len(plan_steps))
                    else:
                        final_response = "I couldn't create a plan for that request. Please provide more details."
                        logger.info("Planning failed - no steps or raw_response", user_id=user_id)
                    
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
                
            elif message_type == "ui_request":
                logger.info("Processing UI request", user_id=user_id)
                agent_used = "ui_agent"
                tools_used = ["dashboard_generator"]
                
                # Generate dashboard data
                dashboard_response = await self.ui_agent.generate_dashboard(user_id)
                dashboard_data = dashboard_response.payload
                
                # Set friendly text response
                final_response = "I've generated your dashboard. You can view your tasks, weather, and daily plan below."
                
                # Return response with data payload
                return {
                    "response": final_response,
                    "agent_used": agent_used,
                    "tools_used": tools_used,
                    "processing_time": time.time() - start_time,
                    "message_type": message_type,
                    "data": dashboard_data
                }
                
            else:
                logger.info("Processing general conversation", user_id=user_id)
                agent_used = "conversation_agent"
                tools_used = ["llm_service"]
                
                # Use the strict LifePilot Planner persona
                final_response = self.llm_service.generate_planner_response(message)
                logger.info("General conversation completed", user_id=user_id)
            
            # Store final response in session context and history
            self.session_service.update_session_context(session_id, "last_response", final_response)
            self.session_service.add_message(session_id, "assistant", final_response)
            
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

# Global RouterAgent instance
_router_agent = None

def get_router_agent() -> RouterAgent:
    """Get global RouterAgent instance"""
    global _router_agent
    if _router_agent is None:
        _router_agent = RouterAgent()
    return _router_agent

def reset_router_agent():
    """Reset RouterAgent instance (for testing)"""
    global _router_agent
    _router_agent = None