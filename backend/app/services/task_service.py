import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models import TaskModel

logger = structlog.get_logger()

class TaskService:
    def __init__(self):
        self.collection_name = "tasks"
    
    @property
    def collection(self):
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized")
        return db[self.collection_name]

    async def create_task(self, user_id: str, task_data: Dict[str, Any]) -> TaskModel:
        """Create a new task"""
        task = TaskModel(user_id=user_id, **task_data)
        task_dict = task.model_dump(by_alias=True, exclude=["id"])
        
        result = await self.collection.insert_one(task_dict)
        
        created_task = await self.collection.find_one({"_id": result.inserted_id})
        return TaskModel(**created_task)

    async def get_tasks(self, user_id: str, filters: Dict[str, Any] = None) -> List[TaskModel]:
        """Get tasks for a user with optional filters"""
        query = {"user_id": user_id}
        if filters:
            query.update(filters)
            
        cursor = self.collection.find(query).sort("created_at", -1)
        tasks = []
        async for doc in cursor:
            tasks.append(TaskModel(**doc))
        return tasks

    async def get_task(self, user_id: str, task_id: str) -> Optional[TaskModel]:
        """Get a single task"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(task_id), "user_id": user_id})
            if doc:
                return TaskModel(**doc)
            return None
        except Exception:
            return None

    async def update_task(self, user_id: str, task_id: str, updates: Dict[str, Any]) -> Optional[TaskModel]:
        """Update a task"""
        updates["updated_at"] = datetime.now()
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(task_id), "user_id": user_id},
                {"$set": updates},
                return_document=True
            )
            
            if result:
                return TaskModel(**result)
            return None
        except Exception as e:
            logger.error("Failed to update task", error=str(e))
            return None

    async def delete_task(self, user_id: str, task_id: str) -> bool:
        """Delete a task"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(task_id), "user_id": user_id})
            return result.deleted_count > 0
        except Exception:
            return False
