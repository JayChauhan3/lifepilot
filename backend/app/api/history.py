from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import structlog
from datetime import datetime
from app.core.database import get_database
from app.models import TaskModel, UserModel
from app.api.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()
logger = structlog.get_logger()

class ChatMessage(BaseModel):
    id: str
    content: str
    role: str
    timestamp: datetime
    agentUsed: Optional[str] = None
    toolsUsed: Optional[List[str]] = None
    processingTime: Optional[float] = None
    messageType: Optional[str] = None

@router.get("/history/tasks", response_model=List[TaskModel])
async def get_task_history(
    current_user: UserModel = Depends(get_current_user),
    limit: int = 50
):
    """
    Get archived tasks history
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not initialized")
            
        archive_collection = db["tasks_archive"]
        
        # Find archived tasks for user, sorted by archived_at (newest first)
        cursor = archive_collection.find(
            {"user_id": current_user.user_id}
        ).sort("archived_at", -1).limit(limit)
        
        tasks = []
        async for doc in cursor:
            tasks.append(TaskModel(**doc))
            
        logger.info("History retrieved", count=len(tasks), user_id=current_user.user_id)
        return tasks
        
    except Exception as e:
        logger.error("Failed to get history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/chat")
async def get_chat_history(
    current_user: UserModel = Depends(get_current_user),
    limit: int = 100
):
    """
    Get chat history for the current user (last 24 hours only)
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not initialized")
            
        chat_collection = db["chat_history"]
        
        # Calculate 24 hours ago
        from datetime import timedelta
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        # Find chat messages for user from last 24 hours, sorted by timestamp (oldest first for chronological order)
        cursor = chat_collection.find(
            {
                "user_id": current_user.user_id,
                "timestamp": {"$gte": twenty_four_hours_ago}
            }
        ).sort("timestamp", 1).limit(limit)
        
        messages = []
        async for doc in cursor:
            messages.append({
                "id": doc.get("id"),
                "content": doc.get("content"),
                "role": doc.get("role"),
                "timestamp": doc.get("timestamp"),
                "agentUsed": doc.get("agentUsed"),
                "toolsUsed": doc.get("toolsUsed"),
                "processingTime": doc.get("processingTime"),
                "messageType": doc.get("messageType"),
            })
            
        logger.info("Chat history retrieved", count=len(messages), user_id=current_user.user_id)
        return {"messages": messages}
        
    except Exception as e:
        logger.error("Failed to get chat history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/history/chat")
async def save_chat_message(
    message: ChatMessage,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Save a chat message to history
    """
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not initialized")
            
        chat_collection = db["chat_history"]
        
        # Save message
        message_doc = {
            "id": message.id,
            "user_id": current_user.user_id,
            "content": message.content,
            "role": message.role,
            "timestamp": message.timestamp,
            "agentUsed": message.agentUsed,
            "toolsUsed": message.toolsUsed,
            "processingTime": message.processingTime,
            "messageType": message.messageType,
        }
        
        await chat_collection.insert_one(message_doc)
        
        logger.info("Chat message saved", user_id=current_user.user_id, message_id=message.id)
        return {"status": "success"}
        
    except Exception as e:
        logger.error("Failed to save chat message", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

