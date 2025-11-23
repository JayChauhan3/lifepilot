import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models import RoutineModel

logger = structlog.get_logger()

class RoutineService:
    def __init__(self):
        self.collection_name = "routines"
    
    @property
    def collection(self):
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized")
        return db[self.collection_name]

    async def create_routine(self, user_id: str, routine_data: Dict[str, Any]) -> RoutineModel:
        """Create a new routine"""
        routine = RoutineModel(user_id=user_id, **routine_data)
        routine_dict = routine.model_dump(by_alias=True, exclude=["id"])
        
        result = await self.collection.insert_one(routine_dict)
        
        created_routine = await self.collection.find_one({"_id": result.inserted_id})
        return RoutineModel(**created_routine)

    async def get_routines(self, user_id: str) -> List[RoutineModel]:
        """Get all routines for a user"""
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        routines = []
        async for doc in cursor:
            routines.append(RoutineModel(**doc))
        return routines

    async def update_routine(self, user_id: str, routine_id: str, updates: Dict[str, Any]) -> Optional[RoutineModel]:
        """Update a routine"""
        updates["updated_at"] = datetime.now()
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(routine_id), "user_id": user_id},
                {"$set": updates},
                return_document=True
            )
            
            if result:
                return RoutineModel(**result)
            return None
        except Exception as e:
            logger.error("Failed to update routine", error=str(e))
            return None

    async def delete_routine(self, user_id: str, routine_id: str) -> bool:
        """Delete a routine"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(routine_id), "user_id": user_id})
            return result.deleted_count > 0
        except Exception:
            return False
