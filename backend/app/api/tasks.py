from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import structlog
from app.services.task_service import TaskService
from app.models import TaskModel, UserModel
from app.api.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()
logger = structlog.get_logger()
task_service = TaskService()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[str] = None
    tags: List[str] = []
    
    # Frontend compatibility fields
    aim: Optional[str] = None
    date: Optional[str] = None
    duration: str  # e.g. "30m", "1h"
    type: Optional[str] = "upcoming"
    priority_index: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[List[str]] = None
    is_completed: Optional[bool] = None
    
    # Frontend compatibility fields
    aim: Optional[str] = None
    date: Optional[str] = None
    duration: Optional[str] = None
    type: Optional[str] = None
    priority_index: Optional[int] = None

class TaskReorder(BaseModel):
    task_ids: List[str]

@router.post("/tasks", response_model=TaskModel)
async def create_task(task: TaskCreate, current_user: UserModel = Depends(get_current_user)):
    """Create a new task"""
    try:
        created_task = await task_service.create_task(current_user.user_id, task.model_dump())
        logger.info("Task created", task_id=str(created_task.id), user_id=current_user.user_id)
        return created_task
    except Exception as e:
        logger.error("Failed to create task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks", response_model=List[TaskModel])
async def get_tasks(
    current_user: UserModel = Depends(get_current_user),
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    """Get all tasks for authenticated user"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
            
        tasks = await task_service.get_tasks(current_user.user_id, filters)
        logger.info("Tasks retrieved", count=len(tasks), user_id=current_user.user_id)
        return tasks
    except Exception as e:
        logger.error("Failed to get tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskModel)
async def get_task(task_id: str, current_user: UserModel = Depends(get_current_user)):
    """Get a single task"""
    try:
        task = await task_service.get_task(current_user.user_id, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/reorder")
async def reorder_tasks(
    reorder_data: TaskReorder,
    current_user: UserModel = Depends(get_current_user)
):
    """Reorder tasks"""
    try:
        await task_service.reorder_tasks(current_user.user_id, reorder_data.task_ids)
        return {"message": "Tasks reordered successfully"}
    except Exception as e:
        logger.error("Failed to reorder tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}", response_model=TaskModel)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update a task"""
    try:
        updates = task_update.model_dump(exclude_unset=True)
        updated_task = await task_service.update_task(current_user.user_id, task_id, updates)
        
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        logger.info("Task updated", task_id=task_id, user_id=current_user.user_id)
        return updated_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: UserModel = Depends(get_current_user)):
    """Delete a task"""
    logger.info("Received delete request for task", task_id=task_id, user_id=current_user.user_id)
    try:
        deleted = await task_service.delete_task(current_user.user_id, task_id)
        if not deleted:
            logger.warning("Task not found for deletion", task_id=task_id)
            raise HTTPException(status_code=404, detail="Task not found")
            
        logger.info("Task deleted", task_id=task_id, user_id=current_user.user_id)
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/sync")
async def sync_tasks(current_user: UserModel = Depends(get_current_user)):
    """Manually trigger task state synchronization"""
    try:
        result = await task_service.sync_user_tasks(current_user.user_id)
        
        logger.info("Tasks synced manually", user_id=current_user.user_id, result=result)
        return result
    except Exception as e:
        logger.error("Failed to sync tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))



