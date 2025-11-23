from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated, Any
from datetime import datetime
from bson import ObjectId

# Helper to handle ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    """Base model for MongoDB documents"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TaskModel(MongoBaseModel):
    """Task document model"""
    user_id: str
    title: str
    description: Optional[str] = None
    status: str = "todo"  # todo, in_progress, done
    priority: str = "medium"  # low, medium, high
    due_date: Optional[datetime] = None
    tags: List[str] = []
    is_completed: bool = False
    
    # Additional metadata
    source: str = "manual"  # manual, ai_generated
    estimated_duration: Optional[int] = None  # in minutes

class RoutineModel(MongoBaseModel):
    """Routine document model"""
    user_id: str
    title: str
    description: Optional[str] = None
    frequency: str = "daily"  # daily, weekly, monthly
    time_of_day: Optional[str] = None  # HH:MM format
    days_of_week: List[str] = []  # mon, tue, etc.
    is_active: bool = True
    
    # Execution tracking
    last_completed_at: Optional[datetime] = None
    streak_count: int = 0

class UserModel(MongoBaseModel):
    """User document model"""
    user_id: str  # External ID (e.g., from Auth provider or simple string)
    email: str
    full_name: Optional[str] = None
    
    # Authentication
    password_hash: Optional[str] = None  # For email/password auth
    oauth_provider: Optional[str] = None  # 'google', 'github', etc.
    oauth_id: Optional[str] = None  # OAuth provider user ID
    
    # User status
    is_active: bool = True
    is_verified: bool = False
    
    # Preferences
    preferences: dict = {}
    
    # System settings
    onboarding_completed: bool = False
