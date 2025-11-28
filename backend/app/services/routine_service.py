import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models import RoutineModel
from app.utils.time_utils import times_overlap, normalize_time_to_24h
from app.utils.seed_routines import seed_default_routines

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

    def _get_id_filter(self, routine_id: str) -> Dict[str, Any]:
        """Create a MongoDB filter for ID that handles both ObjectId and string IDs"""
        try:
            return {"_id": ObjectId(routine_id)}
        except Exception:
            return {"_id": routine_id}

    async def create_routine(self, user_id: str, routine_data: Dict[str, Any]) -> RoutineModel:
        """Create a new routine"""
        # Create the routine model - the model will handle time formatting
        routine = RoutineModel(user_id=user_id, **routine_data)
        
        # Ensure duration is calculated before saving
        if routine.duration is None and routine.startTime and routine.endTime:
            routine.duration = routine.calculate_duration()
        
        # Check for time conflicts
        if routine.startTime and routine.endTime:
            conflicts = await self.find_time_conflicts(
                user_id,
                routine.startTime,
                routine.endTime
            )
            if conflicts:
                conflict_routine = conflicts[0]
                raise ValueError(
                    f"Time conflict with '{conflict_routine.title}' "
                    f"({conflict_routine.startTime} - {conflict_routine.endTime})"
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
        return await seed_default_routines(user_id)

    async def get_routines(self, user_id: str) -> List[RoutineModel]:
        """Get all routines for a user. If none exist, create default routines."""
        # Default routines are created on signup. We just fetch what exists.
        
        # Now fetch all routines
        cursor = self.collection.find({"user_id": user_id}).sort("startTime", 1)
        routines: List[RoutineModel] = []
        
        # Log the raw documents from the database
        raw_docs = []
        async for doc in cursor:
            raw_docs.append(doc)
            
        logger.info(f"Raw routines from database for user {user_id}:", 
                  data=[{k: v for k, v in doc.items() if not k.startswith('_')} for doc in raw_docs])
        
        # Convert to models
        for doc in raw_docs:
            try:
                routine = RoutineModel(**doc)
                routines.append(routine)
                logger.info(f"Converted routine {routine.id}:", 
                          title=routine.title,
                          startTime=routine.startTime,
                          endTime=routine.endTime)
            except Exception as e:
                logger.error(f"Error creating RoutineModel from doc: {e}", doc=doc)
                raise

        return routines
    async def update_routine(self, user_id: str, routine_id: str, updates: Dict[str, Any]) -> Optional[RoutineModel]:
        """Update a routine"""
        # Don't allow updating user_id
        updates.pop('user_id', None)
        
        # Get the existing routine to check for time changes
        id_filter = self._get_id_filter(routine_id)
        existing = await self.collection.find_one({**id_filter, "user_id": user_id})
        if not existing:
            return None
            
        # Check protection flags
        if existing.get("can_edit_title") is False and "title" in updates:
            if updates["title"] != existing["title"]:
                raise ValueError("Title cannot be changed for this routine")
                
        if existing.get("can_edit_time") is False and ("startTime" in updates or "endTime" in updates):
             # Check if times are actually changing
             new_start = updates.get("startTime")
             new_end = updates.get("endTime")
             
             # Get existing times
             old_start = existing.get("startTime")
             old_end = existing.get("endTime")
             
             # If times are changing, raise error
             if (new_start and new_start != old_start) or (new_end and new_end != old_end):
                 raise ValueError("Time cannot be changed for this routine")
        
        # Create a temporary routine model with the updates to properly convert time formats
        temp_updates = {**existing, **updates}
        routine = RoutineModel(**temp_updates)
        
        # Get the properly formatted data from the model
        formatted_updates = routine.model_dump(by_alias=True, exclude=["id", "_id", "created_at"])
        
        # Only include fields that were actually in the updates
        final_updates = {}
        for key in updates.keys():
            if key in formatted_updates:
                final_updates[key] = formatted_updates[key]
        
        # Check for time conflicts if times are being updated
        if 'startTime' in updates or 'endTime' in updates:
            # Get the updated time values, falling back to existing values if not in updates
            start_time = updates.get('startTime', existing.get('startTime'))
            end_time = updates.get('endTime', existing.get('endTime'))
            
            # If we have both time values, check for conflicts
            if start_time and end_time:
                try:
                    # Normalize times to 24h format for comparison
                    norm_start = normalize_time_to_24h(start_time)
                    norm_end = normalize_time_to_24h(end_time)
                    
                    conflicts = await self.find_time_conflicts(
                        user_id,
                        norm_start,
                        norm_end,
                        exclude_id=routine_id
                    )
                    if conflicts:
                        conflict_routine = conflicts[0]
                        raise ValueError(
                            f"Time conflict with '{conflict_routine.title}' "
                            f"({conflict_routine.startTime} - {conflict_routine.endTime})"
                        )
                except Exception as e:
                    logger.error("Error checking time conflicts", error=str(e))
                    raise ValueError("Invalid time format or conflict check failed")
        
        # Add calculated duration if times were updated
        if 'startTime' in updates or 'endTime' in updates:
            final_updates['duration'] = routine.calculate_duration()
        
        # Update the updated_at timestamp
        final_updates['updated_at'] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {**id_filter, "user_id": user_id},
            {"$set": final_updates}
        )
        
        if result.matched_count == 0:
            return None
            
        # Return the updated routine
        updated_routine = await self.collection.find_one({**id_filter, "user_id": user_id})
        return RoutineModel(**updated_routine)
    
    async def find_time_conflicts(
        self,
        user_id: str,
        start_time: str,
        end_time: str,
        exclude_id: Optional[str] = None
    ) -> List[RoutineModel]:
        """
        Find routines that overlap with the given time range
        
        Args:
            user_id: ID of the user
            start_time: Start time in 24h format (e.g., '09:00')
            end_time: End time in 24h format (e.g., '17:00')
            exclude_id: Optional routine ID to exclude from conflict check
            
        Returns:
            List of RoutineModel instances that conflict with the given time range
            
        Raises:
            ValueError: If time format is invalid
        """
        try:
            # Validate input times
            if not start_time or not end_time:
                raise ValueError("Start time and end time are required")
                
            # Normalize input times to 24h format
            try:
                norm_start = normalize_time_to_24h(start_time)
                norm_end = normalize_time_to_24h(end_time)
            except ValueError as e:
                logger.warning("Invalid time format", 
                             start_time=start_time, 
                             end_time=end_time, 
                             error=str(e))
                raise ValueError(f"Invalid time format: {str(e)}")
            
            logger.debug("Checking for time conflicts", 
                        user_id=user_id,
                        input_start=start_time,
                        input_end=end_time,
                        normalized_start=norm_start,
                        normalized_end=norm_end)
            
            # Get all routines for the user
            query = {"user_id": user_id}
            if exclude_id:
                exclusions = [exclude_id]
                try:
                    exclusions.append(ObjectId(exclude_id))
                except Exception:
                    pass
                query["_id"] = {"$nin": exclusions}
            
            cursor = self.collection.find(query)
            conflicts = []
            
            async for doc in cursor:
                try:
                    routine = RoutineModel(**doc)
                    # Skip if routine doesn't have valid times
                    if not routine.startTime or not routine.endTime:
                        continue
                        
                    # Normalize routine times
                    try:
                        existing_start = normalize_time_to_24h(routine.startTime)
                        existing_end = normalize_time_to_24h(routine.endTime)
                    except ValueError as e:
                        logger.warning("Skipping routine with invalid time format", 
                                     routine_id=str(doc.get('_id', 'unknown')),
                                     error=str(e))
                        continue
                    
                    # Check for overlap
                    if times_overlap(norm_start, norm_end, existing_start, existing_end):
                        conflicts.append(routine)
                        logger.debug("Found time conflict", 
                                    routine_id=str(routine.id),
                                    routine_title=routine.title,
                                    routine_times=f"{routine.startTime}-{routine.endTime}")
                        
                except Exception as e:
                    logger.error("Error checking routine times", 
                                routine_id=str(doc.get('_id', 'unknown')),
                                error=str(e))
                    continue
            
            logger.info("Time conflict check completed", 
                       user_id=user_id,
                       conflicts_found=len(conflicts))
            
            return conflicts
            
        except Exception as e:
            logger.error("Error in find_time_conflicts", 
                        error=str(e),
                        user_id=user_id,
                        start_time=start_time,
                        end_time=end_time,
                        stack_info=True)
            raise ValueError(f"Error checking for time conflicts: {str(e)}")


    async def delete_routine(self, user_id: str, routine_id: str) -> bool:
        """Delete a routine"""
        try:
            # Check if routine exists and can be deleted
            id_filter = self._get_id_filter(routine_id)
            routine = await self.collection.find_one({**id_filter, "user_id": user_id})
            if not routine:
                return False
                
            # Check protection flag
            if routine.get("can_delete") is False:
                logger.warning("Attempted to delete protected routine", routine_id=routine_id, user_id=user_id)
                raise ValueError("This routine cannot be deleted")
                
            result = await self.collection.delete_one({**id_filter, "user_id": user_id})
            return result.deleted_count > 0
        except ValueError:
            raise
        except Exception as e:
            logger.error("Failed to delete routine", error=str(e))
            return False
