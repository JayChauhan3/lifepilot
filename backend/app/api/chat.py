 # /api/chat endpoint
from fastapi import APIRouter, HTTPException, Request, Response
import structlog
import uuid
from datetime import datetime, timedelta
from app.schemas import ChatRequest, ChatResponse, AgentMessage
from app.agents.router import RouterAgent, get_router_agent
from app.core.database import get_database

router = APIRouter()
logger = structlog.get_logger()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request, http_response: Response):
    # 1. Session Management
    session_id = req.cookies.get("session_id")
    logger.info("🔍 [CHAT] Incoming request", 
                has_session_cookie=bool(session_id),
                session_id=session_id,
                user_id=request.user_id,
                message_preview=request.message[:50])
    
    if not session_id:
        session_id = str(uuid.uuid4())
        # Set secure HTTP-only cookie
        http_response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=86400, # 24 hours
            secure=False, # Set to True in production with HTTPS
            httponly=True,
            samesite="lax"
        )
        logger.info("✅ [CHAT] Created new session", 
                    session_id=session_id,
                    cookie_max_age=86400)
    else:
        logger.info("♻️ [CHAT] Resumed existing session", session_id=session_id)

    try:
        db = get_database()
        chat_collection = db["chat_messages"] if db is not None else None
        
        logger.info("💾 [CHAT] Database connection", 
                    db_available=db is not None,
                    collection_available=chat_collection is not None)

        # 2. Store User Message
        if chat_collection is not None:
            user_msg = {
                "session_id": session_id,
                "role": "user",
                "content": request.message,
                "timestamp": datetime.utcnow()
            }
            result = await chat_collection.insert_one(user_msg)
            logger.info("✅ [CHAT] Stored user message", 
                        session_id=session_id,
                        message_id=str(result.inserted_id),
                        content_length=len(request.message))
        else:
            logger.warning("⚠️ [CHAT] No database - user message NOT stored")

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
            result = await chat_collection.insert_one(ai_msg)
            logger.info("✅ [CHAT] Stored AI response", 
                        session_id=session_id,
                        message_id=str(result.inserted_id),
                        response_length=len(response_data.get("response", "")),
                        agent_used=response_data.get("agent_used"))
        else:
            logger.warning("⚠️ [CHAT] No database - AI response NOT stored")

        logger.info("🎉 [CHAT] Request completed successfully", 
                    session_id=session_id,
                    total_response_length=len(response_data.get("response", "")))
        
        return ChatResponse(**response_data)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        logger.error("❌ [CHAT] Error processing request", 
                     session_id=session_id,
                     user_id=request.user_id, 
                     error=str(e),
                     error_type=type(e).__name__,
                     stack_trace=error_trace)
        
        # Return more detailed error in development
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {type(e).__name__}: {str(e)}"
        )

@router.get("/chat/history")
async def get_chat_history(req: Request):
    session_id = req.cookies.get("session_id")
    
    logger.info("🔍 [HISTORY] Incoming request", 
                has_session_cookie=bool(session_id),
                session_id=session_id,
                all_cookies=list(req.cookies.keys()))
    
    if not session_id:
        logger.warning("⚠️ [HISTORY] No session_id cookie found - returning empty history")
        return {"messages": []}

    try:
        db = get_database()
        if db is None:
            logger.error("❌ [HISTORY] Database not available")
            return {"messages": []}
            
        chat_collection = db["chat_messages"]
        
        # Calculate 24 hours ago
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        logger.info("💾 [HISTORY] Querying database", 
                    session_id=session_id,
                    cutoff_time=cutoff.isoformat())
        
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
        
        logger.info("✅ [HISTORY] Retrieved messages", 
                    session_id=session_id,
                    message_count=len(messages),
                    roles=[m["role"] for m in messages])
            
        return {"messages": messages}
    except Exception as e:
        logger.error("❌ [HISTORY] Error fetching history", 
                     session_id=session_id, 
                     error=str(e),
                     error_type=type(e).__name__)
        return {"messages": []}