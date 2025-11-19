"""
Long-running task support for LifePilot Backend
Handles pause/resume functionality and task state management
"""

import structlog
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime, timedelta

logger = structlog.get_logger()

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskState:
    """Represents the state of a long-running task"""
    task_id: str
    task_type: str
    status: TaskStatus
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resumed_at: Optional[datetime] = None
    checkpoint_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resumed_at": self.resumed_at.isoformat() if self.resumed_at else None,
            "checkpoint_data": self.checkpoint_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskState":
        task = cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            status=TaskStatus(data["status"]),
            progress=data.get("progress", 0.0),
            result=data.get("result"),
            error=data.get("error"),
            checkpoint_data=data.get("checkpoint_data")
        )
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("resumed_at"):
            task.resumed_at = datetime.fromisoformat(data["resumed_at"])
        return task

class LongRunner:
    """Manages long-running tasks with pause/resume capability"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskState] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    def register_handler(self, task_type: str):
        """Register a handler for a specific task type (decorator usage)"""
        def decorator(handler: Callable):
            self.task_handlers[task_type] = handler
            logger.info("Registered task handler", task_type=task_type)
            return handler
        return decorator
    
    def register_handler_direct(self, task_type: str, handler: Callable):
        """Register a handler for a specific task type (direct usage)"""
        self.task_handlers[task_type] = handler
        logger.info("Registered task handler", task_type=task_type)
    
    async def create_task(self, task_id: str, task_type: str, params: Dict[str, Any]) -> TaskState:
        """Create a new long-running task"""
        if task_id in self.tasks:
            raise ValueError(f"Task {task_id} already exists")
        
        task_state = TaskState(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING
        )
        
        self.tasks[task_id] = task_state
        
        # Start the task
        task_coro = self._execute_task(task_id, task_type, params)
        running_task = asyncio.create_task(task_coro)
        self.running_tasks[task_id] = running_task
        
        logger.info("Created long-running task", task_id=task_id, task_type=task_type)
        return task_state
    
    async def _execute_task(self, task_id: str, task_type: str, params: Dict[str, Any]):
        """Execute a long-running task"""
        task_state = self.tasks[task_id]
        
        try:
            task_state.status = TaskStatus.RUNNING
            task_state.updated_at = datetime.now()
            
            handler = self.task_handlers.get(task_type)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task_type}")
            
            # Execute the handler with checkpoint support
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task_id, params, task_state)
            else:
                result = handler(task_id, params, task_state)
            
            task_state.status = TaskStatus.COMPLETED
            task_state.result = result
            task_state.progress = 100.0
            task_state.updated_at = datetime.now()
            
            logger.info("Task completed", task_id=task_id, result=result)
            
        except asyncio.CancelledError:
            task_state.status = TaskStatus.CANCELLED
            task_state.updated_at = datetime.now()
            logger.info("Task cancelled", task_id=task_id)
            
        except Exception as e:
            task_state.status = TaskStatus.FAILED
            task_state.error = str(e)
            task_state.updated_at = datetime.now()
            logger.error("Task failed", task_id=task_id, error=str(e))
            
        finally:
            # Clean up running task
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def pause_task(self, task_id: str) -> bool:
        """Pause a running task"""
        if task_id not in self.tasks:
            return False
        
        task_state = self.tasks[task_id]
        if task_state.status != TaskStatus.RUNNING:
            return False
        
        # Cancel the running task
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        task_state.status = TaskStatus.PAUSED
        task_state.updated_at = datetime.now()
        
        logger.info("Task paused", task_id=task_id)
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        if task_id not in self.tasks:
            return False
        
        task_state = self.tasks[task_id]
        if task_state.status != TaskStatus.PAUSED:
            return False
        
        task_state.status = TaskStatus.RUNNING
        task_state.resumed_at = datetime.now()
        task_state.updated_at = datetime.now()
        
        # Restart the task with checkpoint data
        params = task_state.checkpoint_data or {}
        task_coro = self._execute_task(task_id, task_state.task_type, params)
        running_task = asyncio.create_task(task_coro)
        self.running_tasks[task_id] = running_task
        
        logger.info("Task resumed", task_id=task_id)
        return True
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        if task_id not in self.tasks:
            return False
        
        # Cancel if running
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        task_state = self.tasks[task_id]
        task_state.status = TaskStatus.CANCELLED
        task_state.updated_at = datetime.now()
        
        logger.info("Task cancelled", task_id=task_id)
        return True
    
    def get_task_status(self, task_id: str) -> Optional[TaskState]:
        """Get the current status of a task"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> Dict[str, TaskState]:
        """List all tasks, optionally filtered by status"""
        if status_filter:
            return {
                task_id: task_state 
                for task_id, task_state in self.tasks.items() 
                if task_state.status == status_filter
            }
        return self.tasks.copy()
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up completed tasks older than max_age_hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task_state in self.tasks.items():
            if (task_state.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
                and task_state.updated_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            logger.info("Cleaned up old task", task_id=task_id)
        
        return len(tasks_to_remove)

# Checkpoint decorator for task handlers
def checkpointable(func):
    """Decorator to add checkpoint support to task handlers"""
    async def wrapper(task_id: str, params: Dict[str, Any], task_state: TaskState):
        checkpoint = task_state.checkpoint_data or {}
        
        # Merge checkpoint data with params
        merged_params = {**checkpoint, **params}
        
        # Call the original function
        if asyncio.iscoroutinefunction(func):
            result = await func(task_id, merged_params, task_state)
        else:
            result = func(task_id, merged_params, task_state)
        
        return result
    
    return wrapper

# Progress update helper
async def update_progress(task_state: TaskState, progress: float, checkpoint_data: Optional[Dict[str, Any]] = None):
    """Update task progress and optionally save checkpoint data"""
    task_state.progress = progress
    task_state.updated_at = datetime.now()
    
    if checkpoint_data:
        task_state.checkpoint_data = checkpoint_data
    
    logger.info("Task progress updated", 
                task_id=task_state.task_id, 
                progress=progress,
                checkpoint_saved=bool(checkpoint_data))

# Global long runner instance
long_runner = LongRunner()