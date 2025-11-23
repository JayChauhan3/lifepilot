import pytest
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.asyncio
class TestRoutinesAPI:
    """Test routines API endpoints"""
    
    async def test_create_routine(self, client: AsyncClient, test_user_id, sample_routine_data):
        """Test creating a routine"""
        response = await client.post(
            f"/api/routines?user_id={test_user_id}",
            json=sample_routine_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_routine_data["title"]
        assert data["user_id"] == test_user_id
        assert "id" in data
    
    async def test_get_routines(self, client: AsyncClient, test_user_id, sample_routine_data):
        """Test getting all routines"""
        # Create a routine first
        await client.post(
            f"/api/routines?user_id={test_user_id}",
            json=sample_routine_data
        )
        
        # Get routines
        response = await client.get(f"/api/routines?user_id={test_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == sample_routine_data["title"]
    
    async def test_update_routine(self, client: AsyncClient, test_user_id, sample_routine_data):
        """Test updating a routine"""
        # Create routine
        create_response = await client.post(
            f"/api/routines?user_id={test_user_id}",
            json=sample_routine_data
        )
        routine_id = create_response.json()["id"]
        
        # Update routine
        updates = {"time_of_day": "09:00", "is_active": False}
        response = await client.put(
            f"/api/routines/{routine_id}?user_id={test_user_id}",
            json=updates
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["time_of_day"] == "09:00"
        assert data["is_active"] is False
    
    async def test_delete_routine(self, client: AsyncClient, test_user_id, sample_routine_data):
        """Test deleting a routine"""
        # Create routine
        create_response = await client.post(
            f"/api/routines?user_id={test_user_id}",
            json=sample_routine_data
        )
        routine_id = create_response.json()["id"]
        
        # Delete routine
        response = await client.delete(f"/api/routines/{routine_id}?user_id={test_user_id}")
        
        assert response.status_code == 200
        
        # Verify deletion
        get_response = await client.get(f"/api/routines?user_id={test_user_id}")
        assert len(get_response.json()) == 0
