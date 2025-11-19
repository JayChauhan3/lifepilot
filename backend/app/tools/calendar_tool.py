# Calendar Tool
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = structlog.get_logger()

class CalendarTool:
    """Mock calendar tool for agent use"""
    
    def __init__(self):
        logger.info("CalendarTool initialized")
        self.events = []
        self._generate_mock_events()
    
    def _generate_mock_events(self):
        """Generate some mock events for demonstration"""
        now = datetime.now()
        self.events = [
            {
                "id": 1,
                "title": "Morning Meditation",
                "start_time": now.replace(hour=7, minute=0, second=0, microsecond=0),
                "end_time": now.replace(hour=7, minute=15, second=0, microsecond=0),
                "description": "Daily mindfulness practice",
                "location": "Home",
                "type": "wellness"
            },
            {
                "id": 2,
                "title": "Team Standup",
                "start_time": now.replace(hour=9, minute=0, second=0, microsecond=0),
                "end_time": now.replace(hour=9, minute=30, second=0, microsecond=0),
                "description": "Daily team sync meeting",
                "location": "Virtual",
                "type": "work"
            },
            {
                "id": 3,
                "title": "Lunch Break",
                "start_time": now.replace(hour=12, minute=0, second=0, microsecond=0),
                "end_time": now.replace(hour=13, minute=0, second=0, microsecond=0),
                "description": "Lunch and rest",
                "location": "Cafeteria",
                "type": "personal"
            }
        ]
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime, 
                    description: str = "", location: str = "", event_type: str = "general") -> Dict[str, Any]:
        """Create a new calendar event"""
        event = {
            "id": len(self.events) + 1,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "location": location,
            "type": event_type,
            "created_at": datetime.now()
        }
        
        self.events.append(event)
        logger.info("Event created", title=title, start_time=start_time)
        return event
    
    def get_events_for_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Get all events for a specific date"""
        target_date = date.date()
        day_events = []
        
        for event in self.events:
            if event["start_time"].date() == target_date:
                day_events.append(event.copy())
        
        # Sort by start time
        day_events.sort(key=lambda x: x["start_time"])
        
        logger.info("Events retrieved for date", date=target_date, count=len(day_events))
        return day_events
    
    def get_events_in_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get events within a date range"""
        events_in_range = []
        
        for event in self.events:
            if start_date.date() <= event["start_time"].date() <= end_date.date():
                events_in_range.append(event.copy())
        
        events_in_range.sort(key=lambda x: x["start_time"])
        
        logger.info("Events retrieved for range", start_date=start_date.date(), end_date=end_date.date(), count=len(events_in_range))
        return events_in_range
    
    def find_available_slots(self, date: datetime, duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """Find available time slots for a given duration"""
        day_events = self.get_events_for_date(date)
        
        # Generate available slots (mock logic)
        available_slots = []
        current_time = date.replace(hour=8, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=18, minute=0, second=0, microsecond=0)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with any event
            is_available = True
            for event in day_events:
                if (current_time < event["end_time"] and slot_end > event["start_time"]):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append({
                    "start_time": current_time,
                    "end_time": slot_end,
                    "duration_minutes": duration_minutes
                })
            
            # Move to next 30-minute slot
            current_time += timedelta(minutes=30)
        
        logger.info("Available slots found", date=date.date(), duration=duration_minutes, slots_count=len(available_slots))
        return available_slots
    
    def update_event(self, event_id: int, **kwargs) -> bool:
        """Update an existing event"""
        for event in self.events:
            if event["id"] == event_id:
                event.update(kwargs)
                event["updated_at"] = datetime.now()
                logger.info("Event updated", event_id=event_id)
                return True
        
        logger.info("Event not found for update", event_id=event_id)
        return False
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event"""
        for i, event in enumerate(self.events):
            if event["id"] == event_id:
                del self.events[i]
                logger.info("Event deleted", event_id=event_id)
                return True
        
        logger.info("Event not found for deletion", event_id=event_id)
        return False