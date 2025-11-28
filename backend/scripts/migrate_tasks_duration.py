import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def migrate_tasks():
    uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(uri)
    db = client.lifepilot_test_db
    
    # Update all tasks that don't have a duration
    result = await db.tasks.update_many(
        {"duration": {"$exists": False}},
        {
            "$set": {"duration": "30m"},
            "$unset": {"time": ""}
        }
    )
    
    print(f"Migrated {result.modified_count} tasks.")
    
    # Also unset time for tasks that might already have duration but still have time
    result_cleanup = await db.tasks.update_many(
        {"time": {"$exists": True}},
        {"$unset": {"time": ""}}
    )
    
    print(f"Cleaned up time field from {result_cleanup.modified_count} tasks.")

if __name__ == "__main__":
    asyncio.run(migrate_tasks())
