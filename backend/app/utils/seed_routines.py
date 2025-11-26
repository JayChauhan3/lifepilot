from typing import List
from app.models import RoutineModel
from app.core.database import db
import structlog

logger = structlog.get_logger()

WORK_BLOCK_DEFAULT_ID = "WORK_BLOCK_DEFAULT_ID"

DEFAULT_ROUTINES = [
    {
        "title": "Morning Routine",
        "time_of_day": "6:00 AM",
        "end_time": "10:00 AM",
        "icon": "FiSun",
        "is_work_block": False,
        "is_protected": False,
        "can_delete": True,
        "can_edit_title": True,
        "can_edit_time": True
    },
    {
        "id": WORK_BLOCK_DEFAULT_ID,
        "title": "Work Block",
        "time_of_day": "10:00 AM",
        "end_time": "5:00 PM",
        "icon": "FiBriefcase",
        "is_work_block": True,
        "is_protected": True,
        "can_delete": False,
        "can_edit_title": False,
        "can_edit_time": True
    },
    {
        "title": "Evening Routine",
        "time_of_day": "5:00 PM",
        "end_time": "10:00 PM",
        "icon": "FiMoon",
        "is_work_block": False,
        "is_protected": False,
        "can_delete": True,
        "can_edit_title": True,
        "can_edit_time": True
    },
    {
        "title": "Sleep",
        "time_of_day": "10:00 PM",
        "end_time": "6:00 AM",
        "icon": "FiMoon",
        "is_work_block": False,
        "is_protected": False,
        "can_delete": True,
        "can_edit_title": True,
        "can_edit_time": True
    }
]

async def seed_default_routines(user_id: str) -> List[RoutineModel]:
    """
    Ensure default routines exist for the user.
    Only creates them if they don't exist.
    Work Block is special: it must exist with the specific ID.
    """
    logger.info("Checking default routines", user_id=user_id)
    
    # Get database instance
    database = db.client[db.db_name] if db.client else None
    if database is None:
        raise RuntimeError("Database not connected")
        
    routines_collection = database.routines
    created_routines = []
    
    # 1. Check/Create Work Block (Mandatory)
    work_block = await routines_collection.find_one({"user_id": user_id, "_id": WORK_BLOCK_DEFAULT_ID})
    print(f"DEBUG: work_block found: {work_block is not None}")
    
    if not work_block:
        logger.info("Seeding Work Block", user_id=user_id)
        work_routine_data = next(r for r in DEFAULT_ROUTINES if r.get("id") == WORK_BLOCK_DEFAULT_ID)
        work_routine = RoutineModel(user_id=user_id, **work_routine_data)
        dumped = work_routine.model_dump(by_alias=True)
        print(f"DEBUG: Dumping Work Block: {dumped.get('_id')}, {dumped.get('id')}")
        await routines_collection.insert_one(dumped)
        created_routines.append(work_routine)
        print("DEBUG: Created Work Block")
    
    # Debug: List all routines
    all_routines = await routines_collection.find({"user_id": user_id}).to_list(length=100)
    print(f"DEBUG: All routines in DB: {[r['_id'] for r in all_routines]}")
    print(f"DEBUG: Type of _id: {[type(r['_id']) for r in all_routines]}")
    
    # Debug: Find what matches the query
    matches = await routines_collection.find({
        "user_id": user_id, 
        "_id": {"$ne": WORK_BLOCK_DEFAULT_ID}
    }).to_list(length=100)
    print(f"DEBUG: Matches for NE query: {[r['_id'] for r in matches]}")

    # 2. Check if user has ANY routines.
    other_routines_count = len(matches)
    print(f"DEBUG: other_routines_count: {other_routines_count}")
    
    if other_routines_count == 0:
        if not work_block: # If work block was missing, it's likely a new user (or broken state).
             logger.info("Seeding other default routines", user_id=user_id)
             print("DEBUG: Seeding other routines...")
             for routine_data in DEFAULT_ROUTINES:
                 if routine_data.get("id") == WORK_BLOCK_DEFAULT_ID:
                     continue # Already handled
                 
                 routine = RoutineModel(user_id=user_id, **routine_data)
                 await routines_collection.insert_one(routine.model_dump(by_alias=True))
                 created_routines.append(routine)
                 print(f"DEBUG: Created {routine.title}")
    
    return created_routines
    
    return created_routines
