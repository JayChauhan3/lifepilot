import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.core.database import db
import os

# Test database name
TEST_DB_NAME = "lifepilot_test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Setup test database"""
    # Override database name for testing
    db.db_name = TEST_DB_NAME
    
    # Connect to test database
    mongo_uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(mongo_uri)
    test_database = client[TEST_DB_NAME]
    
    yield test_database
    
    # Cleanup: Drop test database after all tests
    await client.drop_database(TEST_DB_NAME)
    client.close()

@pytest.fixture
async def client(test_db):
    """Create test client"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.fixture
async def test_user_id():
    """Provide test user ID"""
    return "test_user_123"

@pytest.fixture
async def sample_task_data():
    """Provide sample task data"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "status": "todo",
        "tags": ["test", "sample"]
    }

@pytest.fixture
async def sample_routine_data():
    """Provide sample routine data"""
    return {
        "title": "Test Routine",
        "description": "This is a test routine",
        "frequency": "daily",
        "time_of_day": "08:00",
        "is_active": True
    }

@pytest.fixture(autouse=True)
async def cleanup_collections(test_db):
    """Clean up collections before each test"""
    yield
    # Cleanup after test
    await test_db.tasks.delete_many({})
    await test_db.routines.delete_many({})
    await test_db.users.delete_many({})
