from pydantic import BaseModel, Field, BeforeValidator, model_validator
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
    
    # Frontend compatibility fields
    aim: Optional[str] = None
    date: Optional[str] = None  # YYYY-MM-DD
    duration: str  # e.g. "30m", "1h"
    type: str = "upcoming"  # today, upcoming, done
    priority_index: Optional[int] = None  # For drag-and-drop ordering


def _to_12h(time_str: str) -> str:
    """Convert 24h time string to 12h format"""
    if not time_str:
        return time_str
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime('%-I:%M %p')
    except (ValueError, TypeError):
        return time_str

def _to_24h(time_str: str) -> str:
    """Convert 12h time string to 24h format"""
    if not time_str:
        return time_str
    
    # Try with space first (e.g., "2:00 PM")
    try:
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        return time_obj.strftime('%H:%M')
    except (ValueError, TypeError):
        pass
    
    # Try without space (e.g., "2:00PM")
    try:
        time_obj = datetime.strptime(time_str, '%I:%M%p')
        return time_obj.strftime('%H:%M')
    except (ValueError, TypeError):
        pass
    
    # If both fail, assume it's already in 24h format or invalid
    return time_str

class RoutineModel(MongoBaseModel):
    """Routine document model"""
    user_id: str
    title: str
    description: Optional[str] = None
    frequency: str = "daily"  # daily, weekly, monthly
    startTime: Optional[str] = None  # Internal storage in 24h format (e.g. "09:00")
    endTime: Optional[str] = None  # Internal storage in 24h format (e.g. "17:00")
    days_of_week: List[str] = []  # mon, tue, etc.
    is_active: bool = True
    
    # Display fields for frontend
    duration: Optional[str] = None  # Will be auto-calculated
    is_work_block: bool = False  # Identifies work block routines
    
    # Execution tracking
    last_completed_at: Optional[datetime] = None
    streak_count: int = 0

    # Protection & Permissions
    is_protected: bool = False  # If True, some actions are restricted
    can_delete: bool = True     # If False, cannot be deleted
    can_edit_title: bool = True # If False, title cannot be changed
    can_edit_time: bool = True  # If False, time cannot be changed
    
    class Config:
        """Pydantic config to include computed properties in serialization"""
        from_attributes = True
        populate_by_name = True
    
    
    @model_validator(mode='before')
    @classmethod
    def convert_time_fields(cls, data: Any) -> Any:
        """Convert time fields from 12h to 24h format before validation if needed"""
        if isinstance(data, dict):
            # Handle startTime conversion
            if 'startTime' in data and data['startTime']:
                # If it looks like 12h format (has AM/PM or space), convert it
                if ' ' in data['startTime'] or 'M' in data['startTime'].upper():
                    data['startTime'] = _to_24h(data['startTime'])
            elif 'time_of_day' in data and data['time_of_day']:
                # Handle legacy field input
                data['startTime'] = _to_24h(data['time_of_day'])
                del data['time_of_day']
            
            # Handle endTime conversion
            if 'endTime' in data and data['endTime']:
                # If it looks like 12h format (has AM/PM or space), convert it
                if ' ' in data['endTime'] or 'M' in data['endTime'].upper():
                    data['endTime'] = _to_24h(data['endTime'])
            elif 'end_time' in data and data['end_time']:
                # Handle legacy field input
                data['endTime'] = _to_24h(data['end_time'])
                del data['end_time']
        
        return data
    
    # Removed legacy property accessors to ensure clean API response

    def calculate_duration(self) -> Optional[str]:
        """Calculate duration based on start and end times"""
        if not self.startTime or not self.endTime:
            return None
            
        try:
            # Parse start time (stored as 24h HH:MM)
            start_h, start_m = map(int, self.startTime.split(':'))
            # Parse end time (stored as 24h HH:MM)
            end_h, end_m = map(int, self.endTime.split(':'))
            
            # Calculate total minutes
            total_minutes = (end_h * 60 + end_m) - (start_h * 60 + start_m)
            
            # Handle overnight case
            if total_minutes < 0:
                total_minutes += 24 * 60
                
            # Convert to hours and minutes
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            # Format as "1h 30m" or "45m" or "2h"
            if hours > 0:
                return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
            return f"{minutes}m"
        except (ValueError, IndexError):
            return None

        return data
    
    def model_dump(self, **kwargs):
        """Override to include computed properties and calculate duration"""
        # Use mode='python' to get all fields including private ones
        data = super().model_dump(mode='python', **kwargs)
        
        # Calculate duration if not set
        if self.duration is None and self.startTime and self.endTime:
            self.duration = self.calculate_duration()
        
        # Add computed properties
        data['nextRun'] = self.nextRun
        data['isWorkBlock'] = self.isWorkBlock
        data['duration'] = self.duration or self.calculate_duration()
        
        # Add protection fields
        data['isProtected'] = self.is_protected
        data['canDelete'] = self.can_delete
        data['canEditTitle'] = self.can_edit_title
        data['canEditTime'] = self.can_edit_time
        
        # Remove _id if it is None so Mongo generates it
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        
        # Ensure id is present
        if "id" not in data and "_id" in data:
            data["id"] = str(data["_id"])
        elif "id" in data and isinstance(data["id"], ObjectId):
            data["id"] = str(data["id"])
            
        return data
    
    @property
    def nextRun(self) -> str:
        """Calculate next run time based on frequency and current time"""
        from datetime import datetime, timedelta
        
        if not self.startTime:
            return "Not scheduled"
        
        now = datetime.now()
        time_parts = self.startTime.split(":")
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

    @property
    def isProtected(self) -> bool:
        return self.is_protected

    @property
    def canDelete(self) -> bool:
        return self.can_delete

    @property
    def canEditTitle(self) -> bool:
        return self.can_edit_title

    @property
    def canEditTime(self) -> bool:
        return self.can_edit_time

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
