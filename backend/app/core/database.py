
import certifi
import os
import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = structlog.get_logger()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db_name: str = "lifepilot_db"  # Database name
    is_connected: bool = False  # Connection state tracking

db = Database()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionFailure, ServerSelectionTimeoutError)),
    reraise=True
)
async def connect_to_mongo():
    """Initialize MongoDB connection with retry logic"""
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        logger.warning("MONGODB_URI not set, skipping MongoDB connection")
        return

    try:
        logger.info("Connecting to MongoDB...")
        db.client = AsyncIOMotorClient(
            mongo_uri,
            tlsCAFile=certifi.where(),
            # Connection pool configuration
            maxPoolSize=50,  # Maximum number of connections in the pool
            minPoolSize=10,  # Minimum number of connections to maintain
            maxIdleTimeMS=45000,  # Close idle connections after 45 seconds
            # Timeout configuration
            serverSelectionTimeoutMS=5000,  # Timeout for selecting a server
            connectTimeoutMS=10000,  # Timeout for initial connection
            socketTimeoutMS=45000,  # Timeout for socket operations
        )
        
        # Verify connection
        await db.client.admin.command('ping')
        db.is_connected = True
        logger.info(
            "Successfully connected to MongoDB Atlas",
            pool_size=f"{db.client.options.pool_options.min_pool_size}-{db.client.options.pool_options.max_pool_size}"
        )
        
    except Exception as e:
        db.is_connected = False
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise e

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        db.is_connected = False
        logger.info("MongoDB connection closed")

def get_database():
    """Get database instance"""
    if db.client and db.is_connected:
        return db.client[db.db_name]
    return None

def get_connection_status() -> dict:
    """Get current connection status for health checks"""
    return {
        "connected": db.is_connected,
        "database": db.db_name if db.is_connected else None,
        "client_available": db.client is not None
    }
