# Planner Agent
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.a2a import A2AProtocol
from ..schemas import AgentMessage, PlanPayload
from ..tools.shopping_tool import ShoppingTool
from ..core.llm_service import get_llm_service
from ..core.memory_bank import MemoryBank
from ..core.context_compactor import get_compactor

logger = structlog.get_logger()

class PlannerAgent:
    def __init__(self):
        logger.info("PlannerAgent initialized")
        self.shopping_tool = ShoppingTool()
        self.llm_service = get_llm_service()
        self.memory_bank = MemoryBank()
        self.compactor = get_compactor()
    
    async def create_plan(self, user_message: str, user_id: str = "default", shopping_tool: ShoppingTool = None, context: Dict[str, Any] = None) -> AgentMessage:
        """Create a plan based on user message using RAG"""
        logger.info("Creating plan", user_message=user_message, user_id=user_id)
        
        # Use provided shopping tool or default
        shop_tool = shopping_tool or self.shopping_tool
        
        # Retrieve relevant context using RAG
        context = self.memory_bank.retrieve_relevant_context(user_id, user_message, k=5)
        
        # Compact context if needed
        if context:
            compacted_context = self.compactor.compact_by_token_limit(context, user_message)
        else:
            compacted_context = ""
        
        # Check for shopping-related requests
        if any(keyword in user_message.lower() for keyword in ["buy", "shop", "purchase", "groceries"]):
            # Search for relevant products
            words = user_message.split()
            search_query = " ".join([word for word in words if len(word) > 3])
            products = shop_tool.search_products(search_query)
            
            if products:
                # Add product info to context
                product_info = f"\nAvailable Products:\n"
                for product in products[:3]:
                    product_info += f"- {product['name']}: ${product['price']}\n"
                compacted_context += product_info
        
        # Get chat history for context (if available)
        from ..core.session_service import SessionService
        session_service = SessionService()
        session_id = session_service.get_active_session(user_id)
        
        logger.info("Session retrieved for planner", session_id=session_id, user_id=user_id)
        
        # Retrieve recent conversation history
        chat_history = session_service.get_chat_history(session_id, limit=5)
        
        logger.info("Chat history retrieved", 
                   session_id=session_id,
                   history_count=len(chat_history),
                   history_preview=[{" role": msg["role"], "content": msg["content"][:50]} for msg in chat_history[:2]])
        
        # Format conversation history for LLM context
        conversation_context = ""
        if chat_history:
            conversation_context = "\n\nPrevious conversation:\n"
            for msg in chat_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"
        
        # Combine memory context with conversation history
        full_context = compacted_context + conversation_context
        
        # Debug: Log the context being passed
        logger.info("Context prepared for LLM", 
                   memory_context_length=len(compacted_context), 
                   conversation_context_length=len(conversation_context),
                   full_context_preview=full_context[:300] if full_context else "No context")
        
        # Generate plan using the NEW strict LifePilot Planner persona
        try:
            logger.info("Generating plan with strict planner persona", user_message=user_message, has_conversation_history=bool(chat_history))
            
            # Use the new generate_planner_response method with full context
            raw_response = self.llm_service.generate_planner_response(
                user_message, 
                full_context  # Now includes both memory and conversation history
            )
            
            logger.info("Plan generated successfully", response_length=len(raw_response))
            
            # Create plan payload with raw_response
            plan_payload = PlanPayload(
                user_message=user_message,
                steps=[],  # Empty for now - response is in raw_response
                raw_response=raw_response,  # NEW: Store the full Markdown response
                title="Plan",
                description=user_message[:100],
                priority="medium",
                estimated_duration="As needed",
                context_used=bool(compacted_context),
                llm_generated=True
            )
            
        except Exception as e:
            logger.error("Failed to generate plan with LLM", error=str(e))
            # Fallback: Use a simple error message that follows the planner persona
            fallback_response = """I apologize, but I'm having trouble generating your plan right now.

Please try:
- Being more specific about what you want to plan (e.g., "2-day muscle gain routine")
- Specifying the duration (days, weeks, months)
- Checking your request for clarity

If the problem persists, please try again in a moment."""
            
            plan_payload = PlanPayload(
                user_message=user_message,
                steps=[],
                raw_response=fallback_response,
                title="Error",
                description="Plan generation failed",
                priority="medium",
                estimated_duration="N/A",
                context_used=False,
                llm_generated=False
            )
        
        # Store plan in memory
        self.memory_bank.store_memory(
            user_id=user_id,
            key=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            value={
                "user_message": user_message,
                "raw_response": plan_payload.raw_response,
                "created_at": datetime.now().isoformat()
            },
            category="planning"
        )
        
        # Create response message
        response = A2AProtocol.create_message(
            sender="planner",
            receiver="router",
            message_type="PLAN_RESPONSE",
            payload=plan_payload.dict()
        )
        
        logger.info("Plan created", user_message=user_message, has_raw_response=bool(plan_payload.raw_response), context_used=bool(context))
        return response
    
    def _generate_fallback_steps(self, user_message: str, shopping_tool: ShoppingTool) -> List[str]:
        """Generate fallback steps when LLM is not available"""
        # This method is largely replaced by the try/except block above but kept for safety
        words = user_message.split()
        steps = []
        
        # Check for shopping-related requests
        if any(keyword in user_message.lower() for keyword in ["buy", "shop", "purchase", "groceries"]):
            search_query = " ".join([word for word in words if len(word) > 3])
            products = shopping_tool.search_products(search_query)
            
            if products:
                steps.append(f"Research and compare {search_query} options")
                steps.append(f"Purchase {products[0]['name']} for ${products[0]['price']}")
                steps.append("Schedule delivery or pickup")
            else:
                steps.append("Search for available products")
                steps.append("Compare prices and reviews")
                steps.append("Make purchase decision")
        
        # Morning routine planning
        elif "morning" in user_message.lower() and "routine" in user_message.lower():
            steps = [
                "Wake up at 7:00 AM",
                "Meditate for 10 minutes",
                "Healthy breakfast with oats and fruits",
                "Light exercise or stretching"
            ]
        
        # General planning - IMPROVED to avoid hallucination
        elif "plan" in user_message.lower():
            if len(words) <= 3: # Very short request like "plan my day" without details
                 steps = [
                    "Please share more details about your day",
                    "What are your key priorities?",
                    "Any specific meetings or tasks?"
                ]
            elif len(words) <= 5:
                steps = [
                    f"Research {user_message.replace('plan', '').strip()} requirements",
                    "Create detailed action steps",
                    "Set timeline and milestones"
                ]
            else:
                steps = [
                    "Break down into smaller tasks",
                    "Prioritize by importance and urgency",
                    "Schedule execution time"
                ]
        
        # Default steps
        else:
            steps = [
                "Analyze requirements",
                "Create action plan",
                "Execute and monitor progress"
            ]
        
        # Ensure we have at least 2 steps
        if len(steps) < 2:
            steps.append("Review and adjust as needed")
        
        return steps
    
    async def get_shopping_recommendations(self, query: str, shopping_tool: ShoppingTool = None) -> List[dict]:
        """Get shopping recommendations for planning"""
        logger.info("Getting shopping recommendations", query=query)
        
        shop_tool = shopping_tool or self.shopping_tool
        products = shop_tool.search_products(query)
        
        # Return top 3 recommendations
        recommendations = products[:3] if len(products) > 3 else products
        
        logger.info("Shopping recommendations retrieved", query=query, count=len(recommendations))
        return recommendations

    async def process_task(self, task: str, context: Dict[str, Any] = None) -> AgentMessage:
        """Process a generic planning task"""
        logger.info("Processing planning task", task=task)
        
        # Use LLM to perform the planning task
        try:
            response = self.llm_service.generate_text(
                f"Perform the following planning task: {task}. Provide the result.",
                max_tokens=500
            )
            result = response
            status = "completed"
        except Exception as e:
            logger.error("Failed to process planning task", error=str(e))
            result = f"Failed to process task: {str(e)}"
            status = "failed"
            
        return AgentMessage(
            sender="planner",
            receiver="orchestrator",
            type="PLANNING_RESULT",
            payload={
                "task": task,
                "result": result,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        )
