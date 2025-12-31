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
    
    def _get_routing_tools(self) -> list:
        """Define tools for intelligent routing"""
        return [
            {
                "function_declarations": [
                    {
                        "name": "planning_agent",
                        "description": "Handle requests for creating plans, schedules, routines, roadmaps, or organizing tasks.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "request": {"type": "STRING", "description": "The user's specific planning request"}
                            },
                            "required": ["request"]
                        }
                    },
                    {
                        "name": "memory_store",
                        "description": "Store a new memory, preference, habit, or fact about the user. Use this when the user says 'remember that', 'I like', 'store this', etc.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "content": {"type": "STRING", "description": "The content to remember"}
                            },
                            "required": ["content"]
                        }
                    },
                    {
                        "name": "memory_retrieve",
                        "description": "Retrieve stored memories or answer questions about the user's past, preferences, or profile. Use this for questions like 'what did I say about...', 'do I like...', 'list my memories'.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "query": {"type": "STRING", "description": "The query to search memories for"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "knowledge_search",
                        "description": "Search for external knowledge, facts, news, definitions, or information not personal to the user. Use this for questions like 'who is...', 'search for...', 'find info on...'.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "query": {"type": "STRING", "description": "The search query"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "ui_dashboard",
                        "description": "Show the user's dashboard, interface, or UI. Use this when user asks to 'show dashboard', 'view UI', etc.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {},
                        }
                    }
                ]
            }
        ]

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
        
        agent_used = "conversation_agent"
        tools_used = []
        final_response = ""
        message_type = "general_conversation"

        try:
            # 1. Use Gemini to decide routing via Tool Use
            tools = self._get_routing_tools()
            routing_prompt = f"""You are the Router Agent for LifePilot. Route the user's request to the correct tool.
            
            User Request: "{message}"
            
            If the request is simple conversation or greeting (e.g. "hi", "thanks"), do NOT call any tool. Just reply with text.
            If the request matches a tool's purpose, CALL THAT TOOL.
            """
            
            # Call LLM with tools
            llm_response = self.llm_service.generate_tool_response(routing_prompt, tools=tools)
            
            # Check for function call
            function_call = None
            if hasattr(llm_response, 'candidates') and llm_response.candidates:
                candidate = llm_response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_call = part.function_call
                            break
            
            if function_call:
                tool_name = function_call.name
                tool_args = function_call.args
                logger.info("Gemini selected tool", tool=tool_name, args=tool_args)
                
                if tool_name == "memory_store":
                    message_type = "memory_store"
                    agent_used = "memory_agent"
                    content = tool_args.get("content", message) # Fallback to full message if arg missing
                    
                    # Logic for memory storage with duplicate detection
                    
                    # 1. Cleaning: Remove specific prefixes if they exist in the content (optional, but good for cleanliness)
                    clean_value = content
                    prefixes = [
                        r'^remember\s+that\s+i\s+', r'^remember\s+i\s+', r'^remember\s+that\s+',
                        r'^remember\s+', r'^remember:\s*', r'^store\s+this:\s*',
                        r'^keep\s+in\s+mind:\s*', r'^note\s+that\s+', r'^i\s+prefer\s+'
                    ]
                    for prefix in prefixes:
                        clean_value = re.sub(prefix, '', clean_value, flags=re.IGNORECASE)
                    
                    if clean_value and clean_value[0].islower():
                        clean_value = clean_value[0].upper() + clean_value[1:]
                        
                    # 2. Check for duplicates
                    logger.info("Checking for duplicate memories", user_id=user_id, value=clean_value)
                    
                    is_duplicate = False
                    
                    # A. Check exact match
                    existing_memories = await self.memory_bank.get_all_memories(user_id)
                    clean_value_lower = clean_value.lower().strip()
                    
                    for key, existing_value in existing_memories.items():
                        existing_lower = str(existing_value).lower().strip()
                        if clean_value_lower == existing_lower:
                            is_duplicate = True
                            logger.info("Exact duplicate memory detected", user_id=user_id, existing_key=key)
                            break
                    
                    # B. Check semantic similarity if not exact match
                    if not is_duplicate:
                        try:
                            # Use k=1 to check primarily against the most similar existing memory
                            similar_memories = self.memory_bank.retrieve_similar_memories(user_id, clean_value, k=1)
                            if similar_memories:
                                top_match = similar_memories[0]
                                # Threshold 0.92 indicates extremely high similarity (near duplicate in meaning)
                                if top_match.get("distance", 0) > 0.92:
                                    is_duplicate = True
                                    logger.info("Semantic duplicate detected", user_id=user_id, score=top_match.get("distance"))
                        except Exception as e:
                            logger.warning("Semantic duplicate check failed", error=str(e))
                    
                    if is_duplicate:
                        final_response = f"ℹ️ I already remember that you: {clean_value}. No need to store it again!"
                    else:
                        # Store new memory
                        memory_key = f"memory_{int(time.time())}"
                        memory_response = await self.memory.store_memory(user_id, memory_key, clean_value, "user_stored")
                        
                        if memory_response.payload.get("action") == "stored":
                            final_response = f"✅ I've remembered that: {clean_value}"
                        else:
                            final_response = "❌ Failed to store memory."
                        
                elif tool_name == "memory_retrieve":
                    message_type = "memory_retrieve"
                    agent_used = "memory_agent"
                    query = tool_args.get("query", message)
                    
                    user_memories_dict = await self.memory_bank.get_memories_by_category(user_id, "user_stored")
                    user_memories = [str(v) for v in user_memories_dict.values()]
                    
                    if user_memories:
                        final_response = self.llm_service.generate_memory_response(query, user_memories)
                    else:
                        final_response = "I don't have any specific memories stored about that yet."

                elif tool_name == "knowledge_search":
                    message_type = "knowledge_search"
                    agent_used = "knowledge_agent"
                    query = tool_args.get("query", message)
                    
                    search_results = await self.knowledge.search_knowledge(query, user_id, self.web_search_tool)
                    knowledge_data = search_results.payload.get("results", [])
                    
                    if knowledge_data:
                        formatted_results = []
                        for item in knowledge_data:
                            if isinstance(item, dict):
                                title = item.get('title', 'Untitled')
                                url = item.get('url', '#')
                                formatted_results.append(f"- [{title}]({url})")
                        final_response = f"Found some info:\n" + "\n".join(formatted_results[:3])
                    else:
                        final_response = "I couldn't find relevant information."

                elif tool_name == "planning_agent":
                    message_type = "planning_request"
                    agent_used = "planning_agent"
                    request_text = tool_args.get("request", message)
                    
                    plan_response = await self.planner.create_plan(request_text, user_id)
                    if "raw_response" in plan_response.payload and plan_response.payload["raw_response"]:
                        final_response = plan_response.payload["raw_response"]
                    else:
                        final_response = "I created a plan (fallback view)." # Should rarely hit this with new planner

                elif tool_name == "ui_dashboard":
                    message_type = "ui_request"
                    agent_used = "ui_agent"
                    dashboard_response = await self.ui_agent.generate_dashboard(user_id)
                    final_response = "I've opened your dashboard."
                    return {
                        "response": final_response,
                        "agent_used": agent_used,
                        "data": dashboard_response.payload,
                        "message_type": message_type
                    }

            else:
                # No tool call -> General Conversation
                logger.info("No tool selected, defaulting to conversation")
                if "explain" in message.lower() or "help" in message.lower():
                     # Fallback to standard generation
                     final_response = self.llm_service.generate_text(message)
                else:
                     final_response = self.llm_service.generate_planner_response(message)

            # Store final response
            self.session_service.update_session_context(session_id, "last_response", final_response)
            self.session_service.add_message(session_id, "assistant", final_response)
            
            processing_time = time.time() - start_time
            return {
                "response": final_response,
                "agent_used": agent_used,
                "tools_used": [tool_name] if function_call else [],
                "processing_time": processing_time,
                "message_type": message_type
            }
            
        except Exception as e:
            logger.error("Error processing message", error=str(e))
            import traceback
            logger.error(traceback.format_exc())
            return {
                "response": "I encountered an error. Please try again.",
                "agent_used": "error",
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