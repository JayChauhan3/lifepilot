import structlog
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_database
from app.models import TaskModel

logger = structlog.get_logger()


def get_local_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")


def parse_duration_to_minutes(duration_str: str) -> int:
    """Parse duration string like '1h 30m' or '45m' to total minutes"""
    if not duration_str:
        return 0
    
    total_minutes = 0
    # Match hours
    if 'h' in duration_str:
        hours = int(duration_str.split('h')[0].strip())
        total_minutes += hours * 60
    
    # Match minutes
    if 'm' in duration_str:
        parts = duration_str.split('h')[-1] if 'h' in duration_str else duration_str
        minutes = int(parts.split('m')[0].strip())
        total_minutes += minutes
    
    return total_minutes


def format_duration(total_minutes: int) -> str:
    """Format minutes to 'Xh Ym' string"""
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"


async def move_upcoming_to_today(user_id: str) -> List[str]:
    """
    Move upcoming tasks to today if their date matches current date
    
    Returns:
        List of task IDs that were moved
    """
    db = get_database()
    if db is None:
        raise RuntimeError("Database not initialized")
    
    tasks_collection = db["tasks"]
    today = get_local_date()
    
    # Find upcoming tasks with today's date
    query = {
        "user_id": user_id,
        "type": "upcoming",
        "date": today
    }
    
    # Update them to type="today"
    result = await tasks_collection.update_many(
        query,
        {"$set": {"type": "today", "updated_at": datetime.now()}}
    )
    
    # Get the IDs of moved tasks
    moved_tasks = []
    if result.modified_count > 0:
        cursor = tasks_collection.find({"user_id": user_id, "type": "today", "date": today})
        async for doc in cursor:
            moved_tasks.append(str(doc["_id"]))
    
    logger.info(
        "Moved upcoming tasks to today",
        user_id=user_id,
        count=result.modified_count,
        date=today
    )
    
    return moved_tasks


async def move_unchecked_to_unfinished(user_id: str) -> List[str]:
    """
    Move yesterday's unchecked 'today' tasks to 'unfinished'
    
    Returns:
        List of task IDs that were moved
    """
    db = get_database()
    if db is None:
        raise RuntimeError("Database not initialized")
    
    tasks_collection = db["tasks"]
    today = get_local_date()
    
    # Find today tasks with date < today and not completed
    query = {
        "user_id": user_id,
        "type": "today",
        "date": {"$lt": today},
        "isCompleted": False
    }
    
    # Update them to type="unfinished"
    result = await tasks_collection.update_many(
        query,
        {"$set": {"type": "unfinished", "updated_at": datetime.now()}}
    )
    
    # Get the IDs of moved tasks
    moved_tasks = []
    if result.modified_count > 0:
        cursor = tasks_collection.find({"user_id": user_id, "type": "unfinished"})
        async for doc in cursor:
            moved_tasks.append(str(doc["_id"]))
    
    logger.info(
        "Moved unchecked tasks to unfinished",
        user_id=user_id,
        count=result.modified_count
    )
    
    return moved_tasks


async def check_work_block_capacity(user_id: str) -> Dict[str, Any]:
    """
    Check if today's tasks fit within work block duration
    
    Returns:
        dict with warning flag and message if capacity exceeded
    """
    db = get_database()
    if db is None:
        raise RuntimeError("Database not initialized")
    
    tasks_collection = db["tasks"]
    routines_collection = db["routines"]
    today = get_local_date()
    
    # Get today's tasks
    today_tasks = []
    cursor = tasks_collection.find({"user_id": user_id, "type": "today", "date": today})
    async for doc in cursor:
        today_tasks.append(TaskModel(**doc))
    
    # Calculate total duration
    total_minutes = sum([parse_duration_to_minutes(task.duration) for task in today_tasks])
    
    # Get work block routine
    work_block = await routines_collection.find_one({
        "user_id": user_id,
        "$or": [
            {"isWorkBlock": True},
            {"id": {"$regex": "^WORK_BLOCK"}}
        ]
    })
    
    if not work_block:
        # No work block found, no validation needed
        return {"warning": False}
    
    # Get work block duration
    work_block_minutes = 0
    if work_block.get("duration"):
        work_block_minutes = parse_duration_to_minutes(work_block["duration"])
    elif work_block.get("startTime") and work_block.get("endTime"):
        # Calculate from time range
        start_parts = work_block["startTime"].split(":")
        end_parts = work_block["endTime"].split(":")
        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
        work_block_minutes = end_minutes - start_minutes
    
    # Check if exceeded
    if total_minutes > work_block_minutes:
        return {
            "warning": True,
            "message": "Tasks duration exceeds Work Block. Please adjust timings.",
            "totalDuration": format_duration(total_minutes),
            "workBlockDuration": format_duration(work_block_minutes),
            "exceeded": total_minutes - work_block_minutes
        }
    
    return {
        "warning": False,
        "totalDuration": format_duration(total_minutes),
        "workBlockDuration": format_duration(work_block_minutes)
    }


async def sync_task_states(user_id: str) -> Dict[str, Any]:
    """
    Main sync function - orchestrates all task transitions
    
    Returns:
        dict with sync results and warnings
    """
    try:
        # Step 1: Move unchecked tasks to unfinished (do this first)
        unfinished_ids = await move_unchecked_to_unfinished(user_id)
        
        # Step 2: Move upcoming tasks to today
        today_ids = await move_upcoming_to_today(user_id)
        
        # Step 3: Check work block capacity
        capacity_check = await check_work_block_capacity(user_id)
        
        logger.info(
            "Task sync completed",
            user_id=user_id,
            moved_to_today=len(today_ids),
            moved_to_unfinished=len(unfinished_ids),
            warning=capacity_check.get("warning", False)
        )
        
        return {
            "success": True,
            "movedToToday": len(today_ids),
            "movedToUnfinished": len(unfinished_ids),
            "todayTaskIds": today_ids,
            "unfinishedTaskIds": unfinished_ids,
            **capacity_check
        }
    
    except Exception as e:
        logger.error("Task sync failed", user_id=user_id, error=str(e))
        return {
            "success": False,
            "error": str(e)
        }
