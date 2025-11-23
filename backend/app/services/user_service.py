import structlog
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.database import get_database
from app.models import UserModel

logger = structlog.get_logger()

class UserService:
    def __init__(self):
        self.collection_name = "users"
    
    @property
    def collection(self):
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized")
        return db[self.collection_name]

    async def get_or_create_user(self, user_id: str, email: Optional[str] = None) -> UserModel:
        """Get existing user or create a new one"""
        doc = await self.collection.find_one({"user_id": user_id})
        
        if doc:
            return UserModel(**doc)
        
        # Create new user
        user = UserModel(user_id=user_id, email=email)
        user_dict = user.model_dump(by_alias=True, exclude=["id"])
        
        await self.collection.insert_one(user_dict)
        
        # Fetch again to get the _id
        created_doc = await self.collection.find_one({"user_id": user_id})
        return UserModel(**created_doc)

    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Optional[UserModel]:
        """Update user preferences"""
        try:
            result = await self.collection.find_one_and_update(
                {"user_id": user_id},
                {
                    "$set": {
                        "preferences": preferences,
                        "updated_at": datetime.now()
                    }
                },
                return_document=True
            )
            
            if result:
                return UserModel(**result)
            return None
        except Exception as e:
            logger.error("Failed to update user preferences", error=str(e))
            return None
