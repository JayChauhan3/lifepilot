import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def restore_work_block():
    uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(uri)
    db = client.lifepilot_test_db
    
    user_id = "b797367a-ff68-4688-9c5a-b2631f9a6364"
    routine_id = f"WORK_BLOCK_{user_id}"
    
    routine_data = {
        "_id": routine_id,
        "user_id": user_id,
        "title": "Work Block",
        "startTime": "10:00",
        "endTime": "17:00",
        "duration": "7h",
        "frequency": "daily",
        "days_of_week": ["mon", "tue", "wed", "thu", "fri"],
        "is_active": True,
        "is_work_block": True,
        "is_protected": True,
        "can_delete": False,
        "can_edit_title": False,
        "can_edit_time": True,
        "icon": "FiBriefcase",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    try:
        await db.routines.insert_one(routine_data)
        print(f"Successfully restored Work Block for user {user_id}")
    except Exception as e:
        print(f"Error restoring routine: {e}")

if __name__ == "__main__":
    asyncio.run(restore_work_block())
