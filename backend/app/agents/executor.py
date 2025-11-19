# Executor Agent
import structlog
from datetime import datetime, timedelta
from ..core.a2a import A2AProtocol
from ..schemas import AgentMessage, ExecutionPayload
from ..tools.calendar_tool import CalendarTool

logger = structlog.get_logger()

class ExecutorAgent:
    def __init__(self):
        logger.info("ExecutorAgent initialized")
        self.calendar_tool = CalendarTool()
    
    async def execute_task(self, task: str, calendar_tool: CalendarTool = None) -> AgentMessage:
        """Execute a task using calendar tool for scheduling"""
        logger.info("Executing task", task=task)
        
        # Use provided calendar tool or default
        cal_tool = calendar_tool or self.calendar_tool
        
        # Parse task and create calendar event if scheduling is needed
        execution_result = f"Task '{task}' executed successfully"
        
        # Check if task involves scheduling
        if any(keyword in task.lower() for keyword in ["schedule", "meeting", "appointment", "call"]):
            # Create a calendar event for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
            
            event = cal_tool.create_event(
                title=task,
                start_time=start_time,
                end_time=end_time,
                description=f"Auto-scheduled from task: {task}",
                location="Auto-scheduled",
                event_type="task"
            )
            
            execution_result = f"Task '{task}' scheduled for {start_time.strftime('%Y-%m-%d %H:%M')} (Event ID: {event['id']})"
        
        # Check if task involves checking availability
        elif "available" in task.lower() or "free time" in task.lower():
            tomorrow = datetime.now() + timedelta(days=1)
            available_slots = cal_tool.find_available_slots(tomorrow, duration_minutes=30)
            
            if available_slots:
                slot = available_slots[0]
                execution_result = f"Available tomorrow from {slot['start_time'].strftime('%H:%M')} to {slot['end_time'].strftime('%H:%M')}"
            else:
                execution_result = "No available slots found for tomorrow"
        
        # Create execution payload
        execution_payload = ExecutionPayload(
            task=task,
            result=execution_result,
            status="completed",
            execution_time=datetime.now().isoformat()
        )
        
        # Create response message
        response = A2AProtocol.create_message(
            sender="executor",
            receiver="router",
            message_type="EXECUTION_RESPONSE",
            payload=execution_payload.dict()
        )
        
        logger.info("Task executed", task=task, result=execution_result)
        return response
    
    async def get_scheduled_tasks(self, calendar_tool: CalendarTool = None) -> list:
        """Get all scheduled tasks from calendar"""
        logger.info("Getting scheduled tasks")
        
        cal_tool = calendar_tool or self.calendar_tool
        today = datetime.now()
        events = cal_tool.get_events_for_date(today)
        
        # Filter for task events
        task_events = [event for event in events if event.get("type") == "task"]
        
        logger.info("Scheduled tasks retrieved", count=len(task_events))
        return task_events