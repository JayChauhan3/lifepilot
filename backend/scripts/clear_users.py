import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env vars
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from motor.motor_asyncio import AsyncIOMotorClient

async def clear_users():
    print("Connecting to database...")
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("Error: MONGODB_URI not found in environment variables.")
        return

    client = AsyncIOMotorClient(mongo_uri)
    db_name = "lifepilot_db" # Default or from env
    db = client[db_name]
    collection = db["users"]
    
    count = await collection.count_documents({})
    print(f"Found {count} users.")
    
    if count > 0:
        result = await collection.delete_many({})
        print(f"Deleted {result.deleted_count} users.")
    else:
        print("No users to delete.")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_users())
