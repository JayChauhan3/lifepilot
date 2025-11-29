"""
Task scheduler for automated background jobs
"""
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.utils.task_transitions import sync_task_states
from app.core.database import get_database

logger = structlog.get_logger()

# Create scheduler instance
scheduler = AsyncIOScheduler()


async def get_all_user_ids():
    """Get all user IDs from database"""
    db = get_database()
    if db is None:
        logger.error("Database not initialized for scheduler")
        return []
    
    users_collection = db["users"]
    user_ids = []
    
    cursor = users_collection.find({}, {"user_id": 1})
    async for doc in cursor:
        user_ids.append(doc["user_id"])
    
    return user_ids


async def daily_task_sync_job():
    """
    Scheduled job that runs at midnight to sync all users' task states
    """
    try:
        logger.info("Starting daily task sync job")
        user_ids = await get_all_user_ids()
        
        success_count = 0
        error_count = 0
        
        for user_id in user_ids:
            try:
                result = await sync_task_states(user_id)
                if result.get("success"):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error("Failed to sync user tasks", user_id=user_id, error=str(e))
                error_count += 1
        
        logger.info(
            "Daily task sync completed",
            total_users=len(user_ids),
            success=success_count,
            errors=error_count
        )
    
    except Exception as e:
        logger.error("Daily task sync job failed", error=str(e))


def start_scheduler():
    """Initialize and start the scheduler"""
    # Add midnight cron job (runs at 00:00 every day)
    scheduler.add_job(
        daily_task_sync_job,
        trigger=CronTrigger(hour=0, minute=0),
        id="daily_task_sync",
        name="Daily Task State Sync",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Task scheduler started - daily sync at midnight")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Task scheduler stopped")
