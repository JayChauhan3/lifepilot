import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.task_service import TaskService
from app.services.routine_service import RoutineService
from app.services.user_service import UserService
from app.models import TaskModel, RoutineModel, UserModel
from datetime import datetime

@pytest.mark.unit
class TestTaskServiceUnit:
    """Unit tests for TaskService with mocked database"""
    
    @pytest.fixture
    def mock_collection(self, mocker):
        """Mock MongoDB collection"""
        return mocker.MagicMock()
    
    @pytest.fixture
    def task_service(self, mocker, mock_collection):
        """TaskService with mocked database"""
        service = TaskService()
        mocker.patch.object(service, 'collection', mock_collection)
        return service
    
    @pytest.mark.asyncio
    async def test_create_task_unit(self, task_service, mock_collection):
        """Test task creation without real database"""
        # Mock data
        task_data = {
            "title": "Unit Test Task",
            "description": "Testing without DB",
            "priority": "high"
        }
        user_id = "test_user"
        
        # Mock insert result
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="mock_id_123"))
        mock_collection.find_one = AsyncMock(return_value={
            "_id": "mock_id_123",
            "user_id": user_id,
            "title": task_data["title"],
            "description": task_data["description"],
            "priority": task_data["priority"],
            "status": "todo",
            "tags": [],
            "is_completed": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # Execute
        result = await task_service.create_task(user_id, task_data)
        
        # Assert
        assert result.title == task_data["title"]
        assert result.user_id == user_id
        mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tasks_unit(self, task_service, mock_collection):
        """Test getting tasks without real database"""
        user_id = "test_user"
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        
        # Mock async iteration
        async def mock_async_iter():
            yield {
                "_id": "task1",
                "user_id": user_id,
                "title": "Task 1",
                "status": "todo",
                "priority": "high",
                "tags": [],
                "is_completed": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        
        mock_cursor.__aiter__ = mock_async_iter
        mock_collection.find = MagicMock(return_value=mock_cursor)
        
        # Execute
        tasks = await task_service.get_tasks(user_id)
        
        # Assert
        assert len(tasks) == 1
        assert tasks[0].title == "Task 1"
        mock_collection.find.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_task_unit(self, task_service, mock_collection):
        """Test updating task without real database"""
        user_id = "test_user"
        task_id = "task123"
        updates = {"status": "done"}
        
        # Mock update result
        mock_collection.find_one_and_update = AsyncMock(return_value={
            "_id": task_id,
            "user_id": user_id,
            "title": "Test Task",
            "status": "done",
            "priority": "medium",
            "tags": [],
            "is_completed": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # Execute
        result = await task_service.update_task(user_id, task_id, updates)
        
        # Assert
        assert result.status == "done"
        mock_collection.find_one_and_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_task_unit(self, task_service, mock_collection):
        """Test deleting task without real database"""
        user_id = "test_user"
        task_id = "task123"
        
        # Mock delete result
        mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
        
        # Execute
        result = await task_service.delete_task(user_id, task_id)
        
        # Assert
        assert result is True
        mock_collection.delete_one.assert_called_once()

@pytest.mark.unit
class TestUserServiceUnit:
    """Unit tests for UserService with mocked database"""
    
    @pytest.fixture
    def mock_collection(self, mocker):
        """Mock MongoDB collection"""
        return mocker.MagicMock()
    
    @pytest.fixture
    def user_service(self, mocker, mock_collection):
        """UserService with mocked database"""
        service = UserService()
        mocker.patch.object(service, 'collection', mock_collection)
        return service
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_new_unit(self, user_service, mock_collection):
        """Test creating new user without real database"""
        user_id = "new_user"
        email = "new@example.com"
        
        # Mock user doesn't exist
        mock_collection.find_one = AsyncMock(side_effect=[
            None,  # First call returns None (user doesn't exist)
            {  # Second call returns created user
                "_id": "user123",
                "user_id": user_id,
                "email": email,
                "preferences": {},
                "onboarding_completed": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ])
        mock_collection.insert_one = AsyncMock()
        
        # Execute
        result = await user_service.get_or_create_user(user_id, email)
        
        # Assert
        assert result.user_id == user_id
        assert result.email == email
        mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_or_create_user_existing_unit(self, user_service, mock_collection):
        """Test getting existing user without real database"""
        user_id = "existing_user"
        
        # Mock user exists
        mock_collection.find_one = AsyncMock(return_value={
            "_id": "user123",
            "user_id": user_id,
            "email": "existing@example.com",
            "preferences": {"theme": "dark"},
            "onboarding_completed": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # Execute
        result = await user_service.get_or_create_user(user_id)
        
        # Assert
        assert result.user_id == user_id
        assert result.preferences == {"theme": "dark"}
        mock_collection.find_one.assert_called_once()
