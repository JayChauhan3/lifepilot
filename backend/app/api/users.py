from fastapi import APIRouter, HTTPException, Query, Depends
import structlog
from app.services.user_service import UserService
from app.models import UserModel
from app.api.dependencies import get_current_user
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()
logger = structlog.get_logger()
user_service = UserService()

class PreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]

@router.get("/users/me", response_model=UserModel)
async def get_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    """Get current user profile"""
    logger.info("User profile retrieved", user_id=current_user.user_id)
    return current_user

@router.put("/users/me/preferences", response_model=UserModel)
async def update_preferences(
    prefs: PreferencesUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        updated_user = await user_service.update_preferences(current_user.user_id, prefs.preferences)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        logger.info("User preferences updated", user_id=current_user.user_id)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update preferences", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
