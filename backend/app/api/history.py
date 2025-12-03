from fastapi import APIRouter, HTTPException, Depends
from typing import List
import structlog
from app.core.database import get_database
from app.models import TaskModel, UserModel
from app.api.dependencies import get_current_user

router = APIRouter()
logger = structlog.get_logger()

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



