from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import structlog
from app.services.routine_service import RoutineService
from app.models import RoutineModel, UserModel
from app.api.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()
logger = structlog.get_logger()
routine_service = RoutineService()

class RoutineCreate(BaseModel):
    title: str
    description: Optional[str] = None
    frequency: str = "daily"
    time_of_day: Optional[str] = None
    days_of_week: List[str] = []
    is_active: bool = True
    
    # Display fields
    icon: Optional[str] = None  # Icon identifier (e.g., "FiSun", "FiBriefcase")
    duration: Optional[str] = None  # Display duration (e.g., "45m", "2h", "8h")
    is_work_block: bool = False  # Identifies work block routines

class RoutineUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    time_of_day: Optional[str] = None
    days_of_week: Optional[List[str]] = None
    is_active: Optional[bool] = None
    
    # Display fields
    icon: Optional[str] = None
    duration: Optional[str] = None
    is_work_block: Optional[bool] = None

@router.post("/routines", response_model=RoutineModel)
async def create_routine(routine: RoutineCreate, current_user: UserModel = Depends(get_current_user)):
    """Create a new routine"""
    try:
        created_routine = await routine_service.create_routine(current_user.user_id, routine.model_dump())
        logger.info("Routine created", routine_id=str(created_routine.id), user_id=current_user.user_id)
        return created_routine
    except ValueError as e:
        # Time conflict error
        logger.warning("Routine creation failed - time conflict", error=str(e), user_id=current_user.user_id)
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("Failed to create routine", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routines", response_model=List[RoutineModel])
async def get_routines(current_user: UserModel = Depends(get_current_user)):
    """Get all routines for authenticated user"""
    try:
        routines = await routine_service.get_routines(current_user.user_id)
        logger.info("Routines retrieved", count=len(routines), user_id=current_user.user_id)
        # Explicitly serialize with by_alias=True to ensure frontend compatibility
        return [routine.model_dump(by_alias=True) for routine in routines]
    except Exception as e:
        logger.error("Failed to get routines", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/routines/{routine_id}", response_model=RoutineModel)
async def update_routine(
    routine_id: str,
    routine_update: RoutineUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update a routine"""
    try:
        updates = routine_update.model_dump(exclude_unset=True)
        updated_routine = await routine_service.update_routine(current_user.user_id, routine_id, updates)
        
        if not updated_routine:
            raise HTTPException(status_code=404, detail="Routine not found")
            
        logger.info("Routine updated", routine_id=routine_id, user_id=current_user.user_id)
        return updated_routine
    except ValueError as e:
        # Time conflict error
        logger.warning("Routine update failed - time conflict", error=str(e), user_id=current_user.user_id)
        raise HTTPException(status_code=409, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update routine", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routines/check-conflicts", response_model=List[RoutineModel])
async def check_time_conflicts(
    start_time: str = Query(..., description="Start time in HH:MM format"),
    end_time: str = Query(..., description="End time in HH:MM format"),
    exclude_id: Optional[str] = Query(None, description="Routine ID to exclude from conflict check"),
    current_user: UserModel = Depends(get_current_user)
):
    """Check for time conflicts with existing routines"""
    try:
        # Convert times to 24h format if needed
        from app.utils.time_utils import normalize_time_to_24h
        
        try:
            # First try to normalize the times (handles both 12h and 24h formats)
            norm_start = normalize_time_to_24h(start_time)
            norm_end = normalize_time_to_24h(end_time)
        except ValueError as e:
            logger.warning("Invalid time format", start_time=start_time, end_time=end_time, error=str(e))
            raise HTTPException(status_code=400, detail=f"Invalid time format: {str(e)}")
        
        conflicts = await routine_service.find_time_conflicts(
            current_user.user_id,
            norm_start,
            norm_end,
            exclude_id=exclude_id
        )
        
        logger.info("Conflict check completed", 
                   start_time=start_time,
                   end_time=end_time,
                   normalized_start=norm_start,
                   normalized_end=norm_end,
                   conflicts_found=len(conflicts), 
                   user_id=current_user.user_id)
                   
        return conflicts
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to check conflicts", error=str(e), stack_info=True)
        raise HTTPException(status_code=500, detail="Failed to check for time conflicts")

@router.delete("/routines/{routine_id}")
async def delete_routine(routine_id: str, current_user: UserModel = Depends(get_current_user)):
    """Delete a routine"""
    logger.info("Received delete request for routine", routine_id=routine_id, user_id=current_user.user_id)
    try:
        deleted = await routine_service.delete_routine(current_user.user_id, routine_id)
        if not deleted:
            logger.warning("Routine not found for deletion", routine_id=routine_id)
            raise HTTPException(status_code=404, detail="Routine not found")
            
        logger.info("Routine deleted", routine_id=routine_id, user_id=current_user.user_id)
        return {"message": "Routine deleted successfully"}
    except ValueError as e:
        # Business logic error (e.g. protected routine)
        logger.warning("Routine deletion failed", error=str(e), routine_id=routine_id)
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete routine", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
