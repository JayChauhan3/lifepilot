import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import AuthService
from app.models import UserModel
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_register_creates_pending_user():
    with patch('app.services.auth_service.get_database') as mock_get_db:
        mock_db = MagicMock()
        mock_collection = AsyncMock()
        mock_pending_collection = AsyncMock()
        
        # Mock db["users"] and db["pending_registrations"]
        def get_collection(name):
            if name == "users":
                return mock_collection
            elif name == "pending_registrations":
                return mock_pending_collection
            return AsyncMock()
            
        mock_db.__getitem__.side_effect = get_collection
        mock_get_db.return_value = mock_db
        
        service = AuthService()
        
        # Mock find_one to return None (user doesn't exist)
        mock_collection.find_one.return_value = None
        mock_pending_collection.find_one.return_value = None
        
        # Register
        user = await service.register_user("test@example.com", "Password123!", "Test User")
        
        # Should be inserted into pending_collection, NOT collection
        mock_pending_collection.insert_one.assert_called_once()
        mock_collection.insert_one.assert_not_called()
        
        # User should be returned with is_verified=False
        assert user.email == "test@example.com"
        assert user.is_verified is False

@pytest.mark.asyncio
async def test_verify_email_moves_user_to_main():
    with patch('app.services.auth_service.get_database') as mock_get_db:
        mock_db = MagicMock()
        mock_collection = AsyncMock()
        mock_pending_collection = AsyncMock()
        
        def get_collection(name):
            if name == "users":
                return mock_collection
            elif name == "pending_registrations":
                return mock_pending_collection
            return AsyncMock()
            
        mock_db.__getitem__.side_effect = get_collection
        mock_get_db.return_value = mock_db
        
        service = AuthService()
        
        # Mock pending user
        pending_user = {
            "user_id": "test-id",
            "email": "test@example.com",
            "full_name": "Test User",
            "password_hash": "hashed_secret",
            "verification_token": "ABCDEF",
            "verification_token_expires_at": datetime.utcnow() + timedelta(minutes=15)
        }
        mock_pending_collection.find_one.return_value = pending_user
        mock_collection.find_one.return_value = None # Not in main yet
        
        # Verify
        result = await service.verify_email("test@example.com", "ABCDEF")
        
        assert result is True
        
        # Should insert into main collection
        mock_collection.insert_one.assert_called_once()
        
        # Should delete from pending collection
        mock_pending_collection.delete_one.assert_called_once_with({"email": "test@example.com"})

@pytest.mark.asyncio
async def test_login_unverified_fails():
    with patch('app.services.auth_service.get_database') as mock_get_db:
        mock_db = MagicMock()
        mock_collection = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        service = AuthService()
        
        # User not in main collection (unverified)
        mock_collection.find_one.return_value = None
        
        with pytest.raises(ValueError, match="No account found with this email"):
            await service.authenticate_user("test@example.com", "password")

@pytest.mark.asyncio
async def test_register_existing_pending_resends_link():
    with patch('app.services.auth_service.get_database') as mock_get_db:
        mock_db = MagicMock()
        mock_collection = AsyncMock()
        mock_pending_collection = AsyncMock()
        
        def get_collection(name):
            if name == "users":
                return mock_collection
            elif name == "pending_registrations":
                return mock_pending_collection
            return AsyncMock()
            
        mock_db.__getitem__.side_effect = get_collection
        mock_get_db.return_value = mock_db
        
        service = AuthService()
        
        # Existing pending user
        pending_user = {
            "user_id": "test-id",
            "email": "test@example.com",
            "full_name": "Old Name",
            "password_hash": "old_hash",
            "verification_token": "OLD_TOKEN",
            "verification_token_expires_at": datetime.utcnow()
        }
        
        mock_collection.find_one.return_value = None
        mock_pending_collection.find_one.return_value = pending_user
        
        # Register again
        user = await service.register_user("test@example.com", "NewPass1!", "New Name")
        
        # Should update pending collection
        mock_pending_collection.update_one.assert_called_once()
        call_args = mock_pending_collection.update_one.call_args
        assert call_args[0][0] == {"email": "test@example.com"}
        assert "$set" in call_args[0][1]
        assert "verification_token" in call_args[0][1]["$set"]
        assert call_args[0][1]["$set"]["verification_token"] != "OLD_TOKEN"
