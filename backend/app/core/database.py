
import os
import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

logger = structlog.get_logger()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db_name: str = "lifepilot_db"  # Default DB name

db = Database()

async def connect_to_mongo():
    """Initialize MongoDB connection"""
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        logger.warning("MONGODB_URI not set, skipping MongoDB connection")
        return

    try:
        logger.info("Connecting to MongoDB...")
        db.client = AsyncIOMotorClient(mongo_uri)
        
        # Verify connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
        
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise e

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed")

def get_database():
    """Get database instance"""
    if db.client:
        return db.client[db.db_name]
    return None
