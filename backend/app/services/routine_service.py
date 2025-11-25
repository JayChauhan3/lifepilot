import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models import RoutineModel
from app.utils.time_utils import times_overlap

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
        # Create the routine model - the model will handle time formatting
        routine = RoutineModel(user_id=user_id, **routine_data)
        
        # Ensure duration is calculated before saving
        if routine.duration is None and routine.time_of_day and routine.end_time:
            routine.duration = routine.calculate_duration()
        
        # Check for time conflicts
        if routine._time_of_day and routine._end_time:
            conflicts = await self.find_time_conflicts(
                user_id,
                routine._time_of_day,
                routine._end_time
            )
            if conflicts:
                conflict_routine = conflicts[0]
                raise ValueError(
                    f"Time conflict with '{conflict_routine.title}' "
                    f"({conflict_routine.time_of_day} - {conflict_routine.end_time})"
                )
        
        # Prepare the data for database insertion
        routine_dict = routine.model_dump(by_alias=True, exclude=["id"])
        
        # Insert into database
        result = await self.collection.insert_one(routine_dict)
        
        # Retrieve and return the created routine
        created_routine = await self.collection.find_one({"_id": result.inserted_id})
        return RoutineModel(**created_routine)
    async def create_default_routines(self, user_id: str) -> List[RoutineModel]:
        """Create default routines for a new user"""
        default_routines_data = [
            {
                "title": "Morning Routine",
                "description": "Start the day right with morning activities",
                "frequency": "daily",
                "time_of_day": "06:00",  # 24h format for internal use
                "end_time": "10:00",     # 24h format for internal use
                "startTime": "6:00 AM",  # 12h format for display
                "endTime": "10:00 AM",   # 12h format for display
                "days_of_week": [],
                "is_active": True,
                "icon": "FiSun",
                "is_work_block": False,
                "duration": "4h",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "Work Block",
                "description": "Focused work time",
                "frequency": "daily",
                "time_of_day": "10:00",  # 24h format
                "end_time": "17:00",     # 24h format
                "startTime": "10:00 AM", # 12h format
                "endTime": "5:00 PM",    # 12h format
                "days_of_week": [],
                "is_active": True,
                "icon": "FiBriefcase",
                "is_work_block": True,
                "duration": "7h",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "Evening Routine",
                "description": "Wind down and relax",
                "frequency": "daily",
                "time_of_day": "17:00",  # 24h format
                "end_time": "22:00",     # 24h format
                "startTime": "5:00 PM",  # 12h format
                "endTime": "10:00 PM",   # 12h format
                "days_of_week": [],
                "is_active": True,
                "icon": "FiMoon",
                "is_work_block": False,
                "duration": "5h",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "title": "Sleep",
                "description": "Rest and recharge for the next day",
                "frequency": "daily",
                "time_of_day": "22:00",  # 24h format
                "end_time": "06:00",     # 24h format (next day)
                "startTime": "10:00 PM", # 12h format
                "endTime": "6:00 AM",    # 12h format
                "days_of_week": [],
                "is_active": True,
                "icon": "FiMoon",
                "is_work_block": False,
                "duration": "8h",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        routines = []
        for data in default_routines_data:
            # Create the routine model to trigger duration calculation
            routine = RoutineModel(user_id=user_id, **data)
            
            # Ensure duration is calculated
            if routine.duration is None and routine.time_of_day and routine.end_time:
                routine.duration = routine.calculate_duration()
            
            # Prepare the data for database insertion
            routine_dict = routine.model_dump(by_alias=True, exclude=["id"])
            
            # Insert into database
            result = await self.collection.insert_one(routine_dict)
            
            # Retrieve the created routine
            created_routine = await self.collection.find_one({"_id": result.inserted_id})
            routines.append(RoutineModel(**created_routine))
        
        logger.info("Created default routines for user", user_id=user_id, count=len(routines))
        return routines

    async def get_routines(self, user_id: str) -> List[RoutineModel]:
        """Get all routines for a user. If none exist, create default routines."""
        cursor = self.collection.find({"user_id": user_id}).sort("_time_of_day", 1)
        routines: List[RoutineModel] = []
        async for doc in cursor:
            routines.append(RoutineModel(**doc))

        # Create default routines if none exist
        if not routines:
            routines = await self.create_default_routines(user_id)

        return routines
    async def update_routine(self, user_id: str, routine_id: str, updates: Dict[str, Any]) -> Optional[RoutineModel]:
        """Update a routine"""
        # Don't allow updating user_id
        updates.pop('user_id', None)
        
        # Get the existing routine to check for time changes
        existing = await self.collection.find_one({"_id": ObjectId(routine_id), "user_id": user_id})
        if not existing:
            return None
        
        # Create a temporary routine model with the updates to properly convert time formats
        temp_updates = {**existing, **updates}
        routine = RoutineModel(**temp_updates)
        
        # Get the properly formatted data from the model (this converts time_of_day -> _time_of_day)
        formatted_updates = routine.model_dump(by_alias=True, exclude=["id", "_id", "created_at"])
        
        # Only include fields that were actually in the updates
        final_updates = {}
        for key in updates.keys():
            # Map frontend field names to backend field names
            if key == 'time_of_day' and '_time_of_day' in formatted_updates:
                final_updates['_time_of_day'] = formatted_updates['_time_of_day']
            elif key == 'end_time' and '_end_time' in formatted_updates:
                final_updates['_end_time'] = formatted_updates['_end_time']
            elif key in formatted_updates:
                final_updates[key] = formatted_updates[key]
        
        # Check for time conflicts if times are being updated
        if ('time_of_day' in updates or 'end_time' in updates) and routine._time_of_day and routine._end_time:
            conflicts = await self.find_time_conflicts(
                user_id,
                routine._time_of_day,
                routine._end_time,
                exclude_id=routine_id
            )
            if conflicts:
                conflict_routine = conflicts[0]
                raise ValueError(
                    f"Time conflict with '{conflict_routine.title}' "
                    f"({conflict_routine.time_of_day} - {conflict_routine.end_time})"
                )
        
        # Add calculated duration if times were updated
        if 'time_of_day' in updates or 'end_time' in updates:
            final_updates['duration'] = routine.calculate_duration()
        
        # Update the updated_at timestamp
        final_updates['updated_at'] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(routine_id), "user_id": user_id},
            {"$set": final_updates}
        )
        
        if result.matched_count == 0:
            return None
            
        # Return the updated routine
        updated_routine = await self.collection.find_one({"_id": ObjectId(routine_id)})
        return RoutineModel(**updated_routine)
    
    async def find_time_conflicts(
        self,
        user_id: str,
        start_time: str,
        end_time: str,
        exclude_id: Optional[str] = None
    ) -> List[RoutineModel]:
        """Find routines that overlap with the given time range"""
        # Get all routines for the user
        query = {"user_id": user_id}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        
        cursor = self.collection.find(query)
        conflicts = []
        
        async for doc in cursor:
            routine = RoutineModel(**doc)
            # Check if this routine has times set
            if routine._time_of_day and routine._end_time:
                # Check for overlap
                if times_overlap(start_time, end_time, routine._time_of_day, routine._end_time):
                    conflicts.append(routine)
        
        return conflicts


    async def delete_routine(self, user_id: str, routine_id: str) -> bool:
        """Delete a routine"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(routine_id), "user_id": user_id})
            return result.deleted_count > 0
        except Exception:
            return False
