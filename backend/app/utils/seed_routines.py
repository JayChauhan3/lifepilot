from typing import List
from app.models import RoutineModel
from app.core.database import db
import structlog

logger = structlog.get_logger()

WORK_BLOCK_GLOBAL_ID = "WORK_BLOCK_DEFAULT_ID"

def get_work_block_id(user_id: str) -> str:
    return f"WORK_BLOCK_{user_id}"

DEFAULT_ROUTINES = [
    {
        "title": "Morning Routine",
        "startTime": "06:00",
        "endTime": "10:00",
        "icon": "FiSun",
        "is_work_block": False,
        "is_protected": False,
        "can_delete": True,
        "can_edit_title": True,
        "can_edit_time": True
    },
    {
        "id": "placeholder", # Will be replaced dynamically
        "title": "Work Block",
        "startTime": "10:00",
        "endTime": "17:00",
        "icon": "FiBriefcase",
        "is_work_block": True,
        "is_protected": True,
        "can_delete": False,
        "can_edit_title": False,
        "can_edit_time": True
    },
    {
        "title": "Evening Routine",
        "startTime": "17:00",
        "endTime": "22:00",
        "icon": "FiMoon",
        "is_work_block": False,
        "is_protected": False,
        "can_delete": True,
        "can_edit_title": True,
        "can_edit_time": True
    },
    {
        "title": "Sleep",
        "startTime": "22:00",
        "endTime": "06:00",
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
    
    target_work_block_id = get_work_block_id(user_id)
    
    # 1. Check/Create Work Block (Mandatory)
    work_block = await routines_collection.find_one({"user_id": user_id, "_id": target_work_block_id})
    
    # Get default Work Block data
    default_work_data = next(r for r in DEFAULT_ROUTINES if r.get("title") == "Work Block").copy()
    default_work_data["id"] = target_work_block_id
    
    if not work_block:
        # Check for migration scenarios
        
        # Scenario A: User has the old global ID (WORK_BLOCK_DEFAULT_ID)
        global_work_block = await routines_collection.find_one({"user_id": user_id, "_id": WORK_BLOCK_GLOBAL_ID})
        
        # Scenario B: User has a "Work Block" with a random ID
        legacy_work_block = await routines_collection.find_one({"user_id": user_id, "title": "Work Block"})
        
        existing_to_migrate = global_work_block or legacy_work_block
        
        if existing_to_migrate:
            logger.info("Migrating existing Work Block to user-specific protected ID", user_id=user_id)
            # Preserve existing times
            default_work_data["startTime"] = existing_to_migrate.get("startTime") or existing_to_migrate.get("time_of_day") or existing_to_migrate.get("_time_of_day")
            default_work_data["endTime"] = existing_to_migrate.get("endTime") or existing_to_migrate.get("end_time") or existing_to_migrate.get("_end_time")
            
            # Delete the old one
            await routines_collection.delete_one({"_id": existing_to_migrate["_id"]})
        else:
            logger.info("Seeding Work Block", user_id=user_id)
            
        # Create the new protected Work Block
        work_routine = RoutineModel(user_id=user_id, **default_work_data)
        
        # Ensure _id is set correctly in the dump
        dumped = work_routine.model_dump(by_alias=True)
        if "_id" not in dumped:
            dumped["_id"] = target_work_block_id
            
        await routines_collection.insert_one(dumped)
        created_routines.append(work_routine)
    else:
        # Work Block exists, but check if it has correct protection flags (Fix regression)
        if (work_block.get("can_delete") is not False or 
            work_block.get("is_protected") is not True or 
            work_block.get("can_edit_title") is not False):
            
            logger.info("Fixing protection flags for Work Block", user_id=user_id)
            await routines_collection.update_one(
                {"_id": target_work_block_id},
                {"$set": {
                    "is_protected": True,
                    "can_delete": False,
                    "can_edit_title": False,
                    "can_edit_time": True,
                    "is_work_block": True
                }}
            )
    
    # 2. Check if user has ANY routines.
    other_routines_count = await routines_collection.count_documents({
        "user_id": user_id, 
        "_id": {"$ne": target_work_block_id}
    })
    
    if other_routines_count == 0:
        if not work_block: # If work block was missing (or we just created it), it's likely a new user.
             logger.info("Seeding other default routines", user_id=user_id)
             for routine_data in DEFAULT_ROUTINES:
                 if routine_data.get("title") == "Work Block":
                     continue # Already handled
                 
                 routine = RoutineModel(user_id=user_id, **routine_data)
                 await routines_collection.insert_one(routine.model_dump(by_alias=True))
                 created_routines.append(routine)
    
    return created_routines
