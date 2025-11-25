#!/usr/bin/env python3
"""
Script to clear all collections in the LifePilot database.
Use this for testing purposes to start with a clean database.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from dotenv import load_dotenv

load_dotenv()

async def clear_database():
    """Clear all collections in the database"""
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ MONGODB_URI not set in environment")
        return

    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_uri, tlsCAFile=certifi.where())
    
    try:
        # Get database
        db = client["lifepilot_db"]
        
        # List all collections
        collections = await db.list_collection_names()
        
        if not collections:
            print("✅ Database is already empty")
            return
        
        print(f"\n📋 Found {len(collections)} collection(s):")
        for coll in collections:
            count = await db[coll].count_documents({})
            print(f"  - {coll}: {count} document(s)")
        
        # Confirm deletion
        print("\n⚠️  WARNING: This will delete ALL data from the database!")
        confirm = input("Type 'DELETE' to confirm: ")
        
        if confirm != "DELETE":
            print("❌ Cancelled")
            return
        
        # Drop all collections
        print("\n🗑️  Deleting collections...")
        for coll in collections:
            await db[coll].drop()
            print(f"  ✓ Dropped {coll}")
        
        print("\n✅ Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(clear_database())
