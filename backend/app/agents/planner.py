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
    
    async def create_plan(self, user_message: str, user_id: str = "default", shopping_tool: ShoppingTool = None) -> AgentMessage:
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
        
        # Get chat history from session service
        # Note: PlannerAgent doesn't have direct access to session_service instance in current init
        # We'll need to instantiate it or pass it in. For now, let's instantiate it.
        from ..core.session_service import SessionService
        session_service = SessionService()
        # Assuming user_id is used to create session_id in a standard way, but we need the actual session_id
        # Since we don't have it passed, we might miss history here. 
        # Ideally RouterAgent should pass context.
        # For now, we'll rely on the user_message being descriptive enough or the fallback being smarter.
        
        # Generate plan using LLM
        try:
            # Enhance prompt with instruction to ask for clarification
            enhanced_context = f"{compacted_context}\n\nIMPORTANT: If the user request is vague (e.g. 'plan something'), return a plan with a single step: 'Ask for clarification on what to plan'."
            
            plan_data = self.llm_service.generate_plan(user_message, enhanced_context)
            logger.info("Raw plan data from LLM", plan_data=str(plan_data)[:200])
            
            # Extract steps from plan data
            steps = []
            if "steps" in plan_data:
                for step in plan_data["steps"]:
                    if isinstance(step, dict):
                        steps.append(step.get("action", str(step)))
                    else:
                        steps.append(str(step))
            else:
                # If JSON parsing fails, try to extract steps from the raw response
                response_text = str(plan_data)
                # Split by lines and look for step-like content
                lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                steps = []
                for line in lines:
                    # Skip lines that look like JSON structure
                    if not any(char in line for char in ['{', '}', '[', ']', '"', ':']) and len(line) > 10:
                        steps.append(line)
                
                # If no valid steps found, use Gemini to generate them directly
                if not steps:
                    fallback_response = self.llm_service.generate_text(
                        f"Create 3-4 actionable steps for: {user_message}. If vague, ask for details.",
                        max_tokens=300
                    )
                    steps = [step.strip() for step in fallback_response.split('\n') if step.strip() and len(step.strip()) > 5][:4]
            # Create plan payload
            plan_payload = PlanPayload(
                user_message=user_message,
                steps=steps,
                title=plan_data.get("title", "Action Plan"),
                description=plan_data.get("description", ""),
                priority=plan_data.get("priority", "medium"),
                estimated_duration=plan_data.get("timeline", "As needed"),
                context_used=bool(enhanced_context),
                llm_generated=True
            )
            
        except Exception as e:
            logger.error("Failed to generate plan with LLM", error=str(e))
            # Generate basic fallback without mock templates
            # IMPROVED FALLBACK: Don't hallucinate specific steps for vague requests
            if len(user_message.split()) < 4 and "plan" in user_message.lower():
                 steps = [
                    "Please provide more details about what you'd like to plan",
                    "I can help with daily routines, projects, or shopping",
                    "Let me know your specific goals"
                ]
            else:
                steps = [
                    "Analyze the request and requirements",
                    "Create a structured action plan",
                    "Execute the plan step by step"
                ]
            
            plan_payload = PlanPayload(
                user_message=user_message,
                steps=steps,
                priority="medium",
                estimated_duration="30 minutes",
                context_used=False,
                llm_generated=False
            )
        
        # Store plan in memory
        self.memory_bank.store_memory(
            user_id=user_id,
            key=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            value={
                "user_message": user_message,
                "steps": steps,
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
        
        logger.info("Plan created", user_message=user_message, steps_count=len(steps), context_used=bool(context))
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