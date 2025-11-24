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
        """Get all routines for a user. If none exist, create a default work block routine."""
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        routines: List[RoutineModel] = []
        async for doc in cursor:
            routines.append(RoutineModel(**doc))

        if not routines:
            default_routines_data = [
                {
                    "title": "Morning Routine",
                    "description": "Start the day right",
                    "frequency": "daily",
                    "time_of_day": "07:00",
                    "days_of_week": [],
                    "is_active": True,
                    "icon": "FiSun",
                    "duration": "1h",
                    "is_work_block": False,
                },
                {
                    "title": "Work Block",
                    "description": "Default work block routine",
                    "frequency": "daily",
                    "time_of_day": "09:00",
                    "days_of_week": [],
                    "is_active": True,
                    "icon": "FiBriefcase",
                    "duration": "8h",
                    "is_work_block": True,
                },
                {
                    "title": "Tea Time",
                    "description": "Afternoon break",
                    "frequency": "daily",
                    "time_of_day": "17:00",
                    "days_of_week": [],
                    "is_active": True,
                    "icon": "FiCoffee",
                    "duration": "30m",
                    "is_work_block": False,
                },
                {
                    "title": "Evening Routine",
                    "description": "Wind down for the day",
                    "frequency": "daily",
                    "time_of_day": "18:00",
                    "days_of_week": [],
                    "is_active": True,
                    "icon": "FiMoon",
                    "duration": "1h",
                    "is_work_block": False,
                },
                {
                    "title": "Dinner",
                    "description": "Evening meal",
                    "frequency": "daily",
                    "time_of_day": "20:00",
                    "days_of_week": [],
                    "is_active": True,
                    "icon": "FiShoppingBag",
                    "duration": "1h",
                    "is_work_block": False,
                },
                {
                    "title": "Walk",
                    "description": "Evening walk",
                    "frequency": "daily",
                    "time_of_day": "21:00",
                    "days_of_week": [],
                    "is_active": True,
                    "icon": "FiActivity",
                    "duration": "30m",
                    "is_work_block": False,
                },
                {
                    "title": "Sleep",
                    "description": "Rest and recharge",
                    "frequency": "daily",
                    "time_of_day": "22:00",
                    "days_of_week": [],
                    "is_active": True,
                    "icon": "FiMoon",
                    "duration": "8h",
                    "is_work_block": False,
                }
            ]
            
            for data in default_routines_data:
                routine = await self.create_routine(user_id, data)
                routines.append(routine)

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
