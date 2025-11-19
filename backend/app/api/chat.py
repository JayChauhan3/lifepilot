 # /api/chat endpoint
from fastapi import APIRouter, HTTPException
import structlog
from app.schemas import ChatRequest, ChatResponse, AgentMessage
from app.agents.router import RouterAgent

router = APIRouter()
logger = structlog.get_logger()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info("Chat request received", user_id=request.user_id, message=request.message)
    
    try:
        # Initialize router agent
        router_agent = RouterAgent()
        
        # Process the message through the agent pipeline
        response_data = await router_agent.process_message(request.user_id, request.message)
        
        logger.info("Chat response generated", user_id=request.user_id, response_length=len(response_data.get("response", "")))
        
        return ChatResponse(**response_data)
        
    except Exception as e:
        logger.error("Error processing chat request", user_id=request.user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")