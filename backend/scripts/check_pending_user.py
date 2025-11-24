import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env vars
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from motor.motor_asyncio import AsyncIOMotorClient

async def check_pending_user(email: str):
    print(f"Checking for pending user: {email}")
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("Error: MONGODB_URI not found in environment variables.")
        return

    client = AsyncIOMotorClient(mongo_uri)
    db_name = "lifepilot_db"
    db = client[db_name]
    
    # Check pending collection
    pending_collection = db["pending_registrations"]
    pending_user = await pending_collection.find_one({"email": email})
    
    if pending_user:
        print(f"\n✅ Found in pending_registrations:")
        print(f"   Email: {pending_user.get('email')}")
        print(f"   User ID: {pending_user.get('user_id')}")
        print(f"   Verification Token: {pending_user.get('verification_token')}")
        print(f"   Expires At: {pending_user.get('verification_token_expires_at')}")
        
        # Generate link
        code = pending_user.get('verification_token')
        if code:
            link = f"http://localhost:3000/auth/verify?email={email}&code={code}"
            print(f"\n📧 Verification Link:")
            print(f"   {link}")
    else:
        print(f"\n❌ Not found in pending_registrations")
    
    # Check main collection
    users_collection = db["users"]
    user = await users_collection.find_one({"email": email})
    
    if user:
        print(f"\n✅ Found in users collection:")
        print(f"   Email: {user.get('email')}")
        print(f"   Verified: {user.get('is_verified')}")
    else:
        print(f"\n❌ Not found in users collection")
        
    client.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "opreaction3@gmail.com"
    asyncio.run(check_pending_user(email))
