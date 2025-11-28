import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

async def check_work_block():
    uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(uri)
    db = client.lifepilot_test_db
    
    # Try to find by title or ID
    routines = await db.routines.find({"title": "Work Block"}).to_list(None)
    
    print(f"Found {len(routines)} Work Block routines:")
    for r in routines:
        print(f"ID: {r.get('_id')}")
        print(f"Title: {r.get('title')}")
        print(f"is_work_block: {r.get('is_work_block')}")
        print(f"can_delete: {r.get('can_delete')}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(check_work_block())
