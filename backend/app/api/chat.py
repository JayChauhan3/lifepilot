 # /api/chat endpoint
from fastapi import APIRouter, HTTPException, Request, Response
import structlog
import uuid
from datetime import datetime
from app.schemas import ChatRequest, ChatResponse, AgentMessage
from app.agents.router import RouterAgent, get_router_agent
from app.core.database import get_database

router = APIRouter()
logger = structlog.get_logger()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request, response: Response):
    # 1. Session Management
    session_id = req.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        # Set secure HTTP-only cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=86400, # 24 hours
            secure=False, # Set to True in production with HTTPS
            httponly=True,
            samesite="lax"
        )
        logger.info("Created new session", session_id=session_id)
    else:
        logger.info("Resumed session", session_id=session_id)

    logger.info("Chat request received", user_id=request.user_id, message=request.message, session_id=session_id)
    
    try:
        db = get_database()
        chat_collection = db["chat_messages"] if db is not None else None

        # 2. Store User Message
        if chat_collection is not None:
            user_msg = {
                "session_id": session_id,
                "role": "user",
                "content": request.message,
                "timestamp": datetime.utcnow()
            }
            await chat_collection.insert_one(user_msg)

        # Initialize router agent
        router_agent = get_router_agent()
        
        # Process the message through the agent pipeline
        response_data = await router_agent.process_message(request.user_id, request.message)
        
        # 3. Store AI Response
        if chat_collection is not None:
            ai_msg = {
                "session_id": session_id,
                "role": "assistant",
                "content": response_data.get("response", ""),
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "agent_used": response_data.get("agent_used"),
                    "tools_used": response_data.get("tools_used")
                }
            }
            await chat_collection.insert_one(ai_msg)

        logger.info("Chat response generated", user_id=request.user_id, response_length=len(response_data.get("response", "")))
        
        return ChatResponse(**response_data)
        
    except Exception as e:
        logger.error("Error processing chat request", user_id=request.user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/history")
async def get_chat_history(req: Request):
    session_id = req.cookies.get("session_id")
    if not session_id:
        return {"messages": []}

    try:
        db = get_database()
        if db is None:
            return {"messages": []}
            
        chat_collection = db["chat_messages"]
        
        # Calculate 24 hours ago
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        # Fetch messages
        cursor = chat_collection.find({
            "session_id": session_id,
            "timestamp": {"$gte": cutoff}
        }).sort("timestamp", 1)
        
        messages = []
        async for doc in cursor:
            messages.append({
                "role": doc["role"],
                "content": doc["content"],
                "timestamp": doc["timestamp"]
            })
            
        return {"messages": messages}
    except Exception as e:
        logger.error("Error fetching history", session_id=session_id, error=str(e))
        return {"messages": []}