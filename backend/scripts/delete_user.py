import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env vars
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from motor.motor_asyncio import AsyncIOMotorClient

async def delete_user(email: str):
    print(f"Deleting user: {email}")
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("Error: MONGODB_URI not found in environment variables.")
        return

    client = AsyncIOMotorClient(mongo_uri)
    db_name = "lifepilot_db"
    db = client[db_name]
    
    # Delete from users collection
    users_collection = db["users"]
    result = await users_collection.delete_one({"email": email})
    
    if result.deleted_count > 0:
        print(f"✅ Deleted {result.deleted_count} user(s) from users collection")
    else:
        print(f"❌ No user found in users collection")
    
    # Also check pending
    pending_collection = db["pending_registrations"]
    result2 = await pending_collection.delete_one({"email": email})
    
    if result2.deleted_count > 0:
        print(f"✅ Deleted {result2.deleted_count} user(s) from pending_registrations")
    else:
        print(f"❌ No user found in pending_registrations")
        
    client.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "opreaction3@gmail.com"
    asyncio.run(delete_user(email))
