import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def cleanup_duplicates():
    uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(uri)
    db = client.lifepilot_test_db
    
    # ID of the bad routine (is_work_block: False)
    bad_id = "WORK_BLOCK_b797367a-ff68-4688-9c5a-b2631f9a6364"
    
    result = await db.routines.delete_one({"_id": bad_id})
    
    if result.deleted_count > 0:
        print(f"Successfully deleted duplicate routine: {bad_id}")
    else:
        print(f"Routine not found: {bad_id}")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())
