import pytest
from app.services.task_service import TaskService
from app.services.routine_service import RoutineService
from app.services.user_service import UserService

@pytest.mark.integration
@pytest.mark.asyncio
class TestTaskService:
    """Test task service layer"""
    
    async def test_create_and_get_task(self, test_user_id, sample_task_data):
        """Test creating and retrieving a task"""
        service = TaskService()
        
        # Create task
        task = await service.create_task(test_user_id, sample_task_data)
        assert task.title == sample_task_data["title"]
        assert task.user_id == test_user_id
        
        # Get task
        retrieved_task = await service.get_task(test_user_id, str(task.id))
        assert retrieved_task.id == task.id
        assert retrieved_task.title == task.title
    
    async def test_update_task(self, test_user_id, sample_task_data):
        """Test updating a task"""
        service = TaskService()
        
        # Create task
        task = await service.create_task(test_user_id, sample_task_data)
        
        # Update task
        updates = {"status": "in_progress"}
        updated_task = await service.update_task(test_user_id, str(task.id), updates)
        
        assert updated_task.status == "in_progress"
    
    async def test_delete_task(self, test_user_id, sample_task_data):
        """Test deleting a task"""
        service = TaskService()
        
        # Create task
        task = await service.create_task(test_user_id, sample_task_data)
        
        # Delete task
        deleted = await service.delete_task(test_user_id, str(task.id))
        assert deleted is True
        
        # Verify deletion
        retrieved_task = await service.get_task(test_user_id, str(task.id))
        assert retrieved_task is None

@pytest.mark.integration
@pytest.mark.asyncio
class TestUserService:
    """Test user service layer"""
    
    async def test_get_or_create_user(self, test_user_id):
        """Test user creation"""
        service = UserService()
        
        # Create user
        user = await service.get_or_create_user(test_user_id, "test@example.com")
        assert user.user_id == test_user_id
        assert user.email == "test@example.com"
        
        # Get existing user
        same_user = await service.get_or_create_user(test_user_id)
        assert same_user.id == user.id
    
    async def test_update_preferences(self, test_user_id):
        """Test updating user preferences"""
        service = UserService()
        
        # Create user
        await service.get_or_create_user(test_user_id)
        
        # Update preferences
        prefs = {"theme": "dark", "language": "en"}
        updated_user = await service.update_preferences(test_user_id, prefs)
        
        assert updated_user.preferences == prefs
