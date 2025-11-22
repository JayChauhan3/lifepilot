"""
RoutineLoop Agent for periodic checks and background tasks
Handles cron-like functionality for scheduled operations
"""

import structlog
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.core.a2a import A2AProtocol
from app.core.longrunner import long_runner, TaskStatus, update_progress
from app.schemas import AgentMessage
import json

logger = structlog.get_logger()

@dataclass
class RoutineTask:
    """Represents a scheduled routine task"""
    task_id: str
    name: str
    schedule: str  # Cron-like schedule (e.g., "*/5 * * * *" for every 5 minutes)
    action: str  # Action to perform (e.g., "check_notifications", "cleanup_tasks")
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    
class RoutineAgent:
    """Agent for managing periodic tasks and background operations"""
    
    def __init__(self):
        self.routines: Dict[str, RoutineTask] = {}
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.a2a_protocol = A2AProtocol()
        
        # Register default routines
        self._register_default_routines()
    
    def _register_default_routines(self):
        """Register default periodic tasks"""
        # Check for pending notifications every 5 minutes
        self.add_routine(
            task_id="check_notifications",
            name="Check Notifications",
            schedule="*/5 * * * *",
            action="check_notifications"
        )
        
        # Clean up old tasks every hour
        self.add_routine(
            task_id="cleanup_tasks",
            name="Cleanup Old Tasks",
            schedule="0 * * * *",
            action="cleanup_tasks"
        )
        
        # Health check every 10 minutes
        self.add_routine(
            task_id="health_check",
            name="System Health Check",
            schedule="*/10 * * * *",
            action="health_check"
        )
        
        # Sync data every 30 minutes
        self.add_routine(
            task_id="sync_data",
            name="Data Sync",
            schedule="*/30 * * * *",
            action="sync_data"
        )
    
    def add_routine(self, task_id: str, name: str, schedule: str, action: str, enabled: bool = True):
        """Add a new routine task"""
        routine = RoutineTask(
            task_id=task_id,
            name=name,
            schedule=schedule,
            action=action,
            enabled=enabled
        )
        
        # Calculate next run time
        routine.next_run = self._calculate_next_run(schedule)
        
        self.routines[task_id] = routine
        logger.info("Added routine task", task_id=task_id, name=name, schedule=schedule)
    
    def remove_routine(self, task_id: str) -> bool:
        """Remove a routine task"""
        if task_id in self.routines:
            del self.routines[task_id]
            logger.info("Removed routine task", task_id=task_id)
            return True
        return False
    
    def enable_routine(self, task_id: str) -> bool:
        """Enable a routine task"""
        if task_id in self.routines:
            self.routines[task_id].enabled = True
            logger.info("Enabled routine task", task_id=task_id)
            return True
        return False
    
    def disable_routine(self, task_id: str) -> bool:
        """Disable a routine task"""
        if task_id in self.routines:
            self.routines[task_id].enabled = False
            logger.info("Disabled routine task", task_id=task_id)
            return True
        return False
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time from cron-like schedule"""
        # Simple implementation for common patterns
        # Format: "*/X * * * *" where X is minutes
        if schedule.startswith("*/"):
            minutes = int(schedule.split("*/")[1].split(" ")[0])
            next_run = datetime.now() + timedelta(minutes=minutes)
            # Round to the next minute boundary
            next_run = next_run.replace(second=0, microsecond=0)
            return next_run
        
        # For hourly: "0 * * * *"
        if schedule == "0 * * * *":
            next_run = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return next_run
        
        # Default: run in 1 hour
        return datetime.now() + timedelta(hours=1)
    
    async def start_scheduler(self):
        """Start the routine scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Routine scheduler started")
    
    async def stop_scheduler(self):
        """Stop the routine scheduler"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Routine scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check which routines need to run
                for routine in self.routines.values():
                    if (routine.enabled and 
                        routine.next_run and 
                        current_time >= routine.next_run):
                        
                        # Run the routine
                        await self._execute_routine(routine)
                        
                        # Update schedule
                        routine.last_run = current_time
                        routine.next_run = self._calculate_next_run(routine.schedule)
                        routine.run_count += 1
                
                # Sleep for 1 minute before next check
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Scheduler loop error", error=str(e))
                await asyncio.sleep(60)
    
    async def _execute_routine(self, routine: RoutineTask):
        """Execute a routine task"""
        logger.info("Executing routine", 
                   task_id=routine.task_id, 
                   name=routine.name, 
                   action=routine.action)
        
        try:
            if routine.action == "check_notifications":
                await self._check_notifications()
            elif routine.action == "cleanup_tasks":
                await self._cleanup_tasks()
            elif routine.action == "health_check":
                await self._health_check()
            elif routine.action == "sync_data":
                await self._sync_data()
            else:
                logger.warning("Unknown routine action", action=routine.action)
                
        except Exception as e:
            logger.error("Routine execution failed", 
                        task_id=routine.task_id, 
                        error=str(e))
    
    async def _check_notifications(self):
        """Check for pending notifications and send them"""
        logger.info("Checking notifications")
        
        # Use NotificationAgent to send alerts
        # In a real scenario, we might check a DB for pending alerts
        # For now, we'll simulate a periodic check
        
        from app.agents.notifications import NotificationAgent
        # Note: In a real app, we should inject this or get it from a container
        # For now, we'll instantiate it or use a singleton if available
        notification_agent = NotificationAgent()
        
        # Check for pending alerts (this is just a placeholder logic)
        # We could also generate system alerts here
        
        # Example: Send a heartbeat alert if needed
        # await notification_agent.send_alert("system", "Routine check completed", "low")
        
        logger.info("Notification check completed")
    
    async def _cleanup_tasks(self):
        """Clean up old completed tasks"""
        logger.info("Cleaning up old tasks")
        
        # Clean up long runner tasks
        cleaned_count = long_runner.cleanup_completed_tasks(max_age_hours=24)
        logger.info("Cleaned up old tasks", count=cleaned_count)
    
    async def _health_check(self):
        """Perform system health check"""
        logger.info("Performing health check")
        
        # Check long runner status
        running_tasks = len(long_runner.running_tasks)
        total_tasks = len(long_runner.tasks)
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "running_tasks": running_tasks,
            "total_tasks": total_tasks,
            "active_routines": len([r for r in self.routines.values() if r.enabled]),
            "scheduler_running": self.running
        }
        
        logger.info("Health check completed", **health_status)
        
        # Store health status for monitoring
        return health_status
    
    async def _sync_data(self):
        """Sync data with external systems"""
        logger.info("Syncing data")
        
        # Create a long-running task for data sync
        task_id = f"sync_data_{int(datetime.now().timestamp())}"
        
        try:
            await long_runner.create_task(
                task_id=task_id,
                task_type="data_sync",
                params={"sync_type": "full_sync"}
            )
            
            logger.info("Data sync task created", task_id=task_id)
            
        except Exception as e:
            logger.error("Failed to create data sync task", error=str(e))
    
    async def trigger_routine(self, task_id: str) -> bool:
        """Manually trigger a routine task"""
        if task_id not in self.routines:
            logger.warning("Routine not found", task_id=task_id)
            return False
        
        routine = self.routines[task_id]
        await self._execute_routine(routine)
        
        logger.info("Manually triggered routine", task_id=task_id)
        return True
    
    def get_routine_status(self) -> Dict[str, Any]:
        """Get status of all routine tasks"""
        return {
            "scheduler_running": self.running,
            "total_routines": len(self.routines),
            "active_routines": len([r for r in self.routines.values() if r.enabled]),
            "routines": {
                task_id: {
                    "name": routine.name,
                    "schedule": routine.schedule,
                    "enabled": routine.enabled,
                    "last_run": routine.last_run.isoformat() if routine.last_run else None,
                    "next_run": routine.next_run.isoformat() if routine.next_run else None,
                    "run_count": routine.run_count
                }
                for task_id, routine in self.routines.items()
            }
        }
    
    async def create_long_running_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """Create a long-running task from routine context"""
        task_id = f"{task_type}_{int(datetime.now().timestamp())}"
        
        await long_runner.create_task(
            task_id=task_id,
            task_type=task_type,
            params=params
        )
        
        logger.info("Created long-running task from routine", 
                   task_id=task_id, 
                   task_type=task_type)
        
        return task_id

# Register long-running task handlers
@long_runner.register_handler("data_sync")
async def handle_data_sync(task_id: str, params: Dict[str, Any], task_state):
    """Handle data synchronization task"""
    logger.info("Starting data sync", task_id=task_id)
    
    try:
        # Simulate data sync progress
        steps = ["validating_data", "syncing_users", "syncing_tasks", "syncing_logs", "finalizing"]
        
        for i, step in enumerate(steps):
            await update_progress(task_state, (i + 1) / len(steps) * 100, 
                                {"current_step": step, "synced_items": i * 10})
            
            # Simulate work
            await asyncio.sleep(1)
        
        result = {
            "synced_items": 40,
            "sync_duration_seconds": 5,
            "status": "completed"
        }
        
        logger.info("Data sync completed", task_id=task_id, result=result)
        return result
        
    except Exception as e:
        logger.error("Data sync failed", task_id=task_id, error=str(e))
        raise

# Global routine agent instance
routine_agent = RoutineAgent()