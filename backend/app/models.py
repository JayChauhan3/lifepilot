from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated, Any
from datetime import datetime
from bson import ObjectId

# Helper to handle ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class MongoBaseModel(BaseModel):
    """Base model for MongoDB documents"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None, serialization_alias="id")
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
    
    # Frontend compatibility fields
    aim: Optional[str] = None
    date: Optional[str] = None  # YYYY-MM-DD
    time: Optional[str] = None  # HH:mm
    type: str = "upcoming"  # today, upcoming, done

class RoutineModel(MongoBaseModel):
    """Routine document model"""
    user_id: str
    title: str
    description: Optional[str] = None
    frequency: str = "daily"  # daily, weekly, monthly
    time_of_day: Optional[str] = None  # HH:MM format
    days_of_week: List[str] = []  # mon, tue, etc.
    is_active: bool = True
    
    # Display fields for frontend
    icon: Optional[str] = None  # Icon identifier (e.g., "FiSun", "FiBriefcase")
    duration: Optional[str] = None  # Display duration (e.g., "45m", "2h", "8h")
    is_work_block: bool = False  # Identifies work block routines
    
    # Execution tracking
    last_completed_at: Optional[datetime] = None
    streak_count: int = 0
    
    class Config:
        """Pydantic config to include computed properties in serialization"""
        from_attributes = True
        populate_by_name = True
    
    def model_dump(self, **kwargs):
        """Override to include computed properties"""
        data = super().model_dump(**kwargs)
        # Add computed properties
        data['startTime'] = self.startTime
        data['nextRun'] = self.nextRun
        data['isWorkBlock'] = self.isWorkBlock
        
        # Ensure id is present (fix for serialization issue)
        if "id" not in data and "_id" in data:
            data["id"] = str(data["_id"])
        elif "id" in data and isinstance(data["id"], ObjectId):
            data["id"] = str(data["id"])
            
        return data
    
    @property
    def startTime(self) -> Optional[str]:
        """Alias for time_of_day for frontend compatibility"""
        return self.time_of_day
    
    @property
    def nextRun(self) -> str:
        """Calculate next run time based on frequency and current time"""
        from datetime import datetime, timedelta
        
        if not self.time_of_day:
            return "Not scheduled"
        
        now = datetime.now()
        time_parts = self.time_of_day.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # Create today's scheduled time
        scheduled_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if self.frequency == "daily":
            # If today's time has passed, schedule for tomorrow
            if now > scheduled_today:
                next_time = scheduled_today + timedelta(days=1)
            else:
                next_time = scheduled_today
            return "Tomorrow" if now > scheduled_today else "Today"
        
        elif self.frequency == "weekly":
            # Find next occurrence based on days_of_week
            if not self.days_of_week:
                return "Not scheduled"
            
            day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
            current_weekday = now.weekday()
            
            # Find the next scheduled day
            scheduled_days = sorted([day_map.get(day.lower(), -1) for day in self.days_of_week if day.lower() in day_map])
            
            if not scheduled_days:
                return "Not scheduled"
            
            # Find next day
            for day in scheduled_days:
                if day > current_weekday or (day == current_weekday and now < scheduled_today):
                    days_ahead = day - current_weekday
                    return f"In {days_ahead} days" if days_ahead > 1 else "Tomorrow" if days_ahead == 1 else "Today"
            
            # If no day found this week, use first day of next week
            days_ahead = (7 - current_weekday) + scheduled_days[0]
            return f"In {days_ahead} days"
        
        elif self.frequency == "monthly":
            # Simple monthly calculation
            if now > scheduled_today:
                return "Next month"
            else:
                return "This month"
        
        return "Scheduled"
    
    @property
    def isWorkBlock(self) -> bool:
        """Alias for is_work_block for frontend compatibility"""
        return self.is_work_block

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
    verification_token: Optional[str] = None
    verification_token_expires_at: Optional[datetime] = None
    
    # Preferences
    preferences: dict = {}
    
    # System settings
    onboarding_completed: bool = False
