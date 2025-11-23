import pytest
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.asyncio
class TestTasksAPI:
    """Test tasks API endpoints"""
    
    async def test_create_task(self, client: AsyncClient, test_user_id, sample_task_data):
        """Test creating a task"""
        response = await client.post(
            f"/api/tasks?user_id={test_user_id}",
            json=sample_task_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["user_id"] == test_user_id
        assert "id" in data
    
    async def test_get_tasks(self, client: AsyncClient, test_user_id, sample_task_data):
        """Test getting all tasks"""
        # Create a task first
        await client.post(
            f"/api/tasks?user_id={test_user_id}",
            json=sample_task_data
        )
        
        # Get tasks
        response = await client.get(f"/api/tasks?user_id={test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == sample_task_data["title"]
    
    async def test_get_task_by_id(self, client: AsyncClient, test_user_id, sample_task_data):
        """Test getting a single task"""
        # Create task
        create_response = await client.post(
            f"/api/tasks?user_id={test_user_id}",
            json=sample_task_data
        )
        task_id = create_response.json()["id"]
        
        # Get task by ID
        response = await client.get(f"/api/tasks/{task_id}?user_id={test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == sample_task_data["title"]
    
    async def test_update_task(self, client: AsyncClient, test_user_id, sample_task_data):
        """Test updating a task"""
        # Create task
        create_response = await client.post(
            f"/api/tasks?user_id={test_user_id}",
            json=sample_task_data
        )
        task_id = create_response.json()["id"]
        
        # Update task
        updates = {"status": "done", "is_completed": True}
        response = await client.put(
            f"/api/tasks/{task_id}?user_id={test_user_id}",
            json=updates
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"
        assert data["is_completed"] is True
    
    async def test_delete_task(self, client: AsyncClient, test_user_id, sample_task_data):
        """Test deleting a task"""
        # Create task
        create_response = await client.post(
            f"/api/tasks?user_id={test_user_id}",
            json=sample_task_data
        )
        task_id = create_response.json()["id"]
        
        # Delete task
        response = await client.delete(f"/api/tasks/{task_id}?user_id={test_user_id}")
        
        assert response.status_code == 200
        
        # Verify deletion
        get_response = await client.get(f"/api/tasks/{task_id}?user_id={test_user_id}")
        assert get_response.status_code == 404
    
    async def test_get_tasks_with_filters(self, client: AsyncClient, test_user_id):
        """Test getting tasks with filters"""
        # Create tasks with different statuses
        await client.post(
            f"/api/tasks?user_id={test_user_id}",
            json={"title": "Task 1", "status": "todo", "priority": "high"}
        )
        await client.post(
            f"/api/tasks?user_id={test_user_id}",
            json={"title": "Task 2", "status": "done", "priority": "low"}
        )
        
        # Filter by status
        response = await client.get(f"/api/tasks?user_id={test_user_id}&status=todo")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "todo"
