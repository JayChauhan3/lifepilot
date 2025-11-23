import structlog
from typing import Optional
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.core.database import get_database
from app.models import UserModel
from datetime import datetime
import uuid

logger = structlog.get_logger()

# OAuth configuration
config = Config('.env')
oauth = OAuth(config)

# Register Google OAuth
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

class OAuthService:
    def __init__(self):
        self.collection_name = "users"
    
    @property
    def collection(self):
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized")
        return db[self.collection_name]
    
    async def get_user_by_oauth(self, oauth_provider: str, oauth_id: str) -> Optional[UserModel]:
        """Get user by OAuth provider and ID"""
        try:
            doc = await self.collection.find_one({
                "oauth_provider": oauth_provider,
                "oauth_id": oauth_id
            })
            if doc:
                return UserModel(**doc)
            return None
        except Exception as e:
            logger.error("Failed to get user by OAuth", error=str(e))
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        try:
            doc = await self.collection.find_one({"email": email})
            if doc:
                return UserModel(**doc)
            return None
        except Exception as e:
            logger.error("Failed to get user by email", error=str(e))
            return None
    
    async def create_or_update_oauth_user(
        self,
        email: str,
        oauth_provider: str,
        oauth_id: str,
        full_name: Optional[str] = None
    ) -> UserModel:
        """
        Create or update user from OAuth login
        
        Args:
            email: User email from OAuth provider
            oauth_provider: OAuth provider name (e.g., 'google')
            oauth_id: User ID from OAuth provider
            full_name: Optional full name
            
        Returns:
            UserModel (created or existing)
        """
        # Check if user exists by OAuth ID
        existing_user = await self.get_user_by_oauth(oauth_provider, oauth_id)
        
        if existing_user:
            # Update user info if needed
            updates = {
                "updated_at": datetime.now()
            }
            if full_name and not existing_user.full_name:
                updates["full_name"] = full_name
            
            await self.collection.update_one(
                {"user_id": existing_user.user_id},
                {"$set": updates}
            )
            
            logger.info("OAuth user logged in", email=email, provider=oauth_provider)
            return existing_user
        
        # Check if user exists by email (link accounts)
        existing_user_by_email = await self.get_user_by_email(email)
        
        if existing_user_by_email:
            # Link OAuth to existing account
            updates = {
                "oauth_provider": oauth_provider,
                "oauth_id": oauth_id,
                "is_verified": True,
                "updated_at": datetime.now()
            }
            
            await self.collection.update_one(
                {"user_id": existing_user_by_email.user_id},
                {"$set": updates}
            )
            
            logger.info("OAuth linked to existing account", email=email, provider=oauth_provider)
            
            # Fetch updated user
            updated_doc = await self.collection.find_one({"user_id": existing_user_by_email.user_id})
            return UserModel(**updated_doc)
        
        # Create new user
        user_id = str(uuid.uuid4())
        
        user = UserModel(
            user_id=user_id,
            email=email,
            full_name=full_name,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            is_active=True,
            is_verified=True  # OAuth users are auto-verified
        )
        
        user_dict = user.model_dump(by_alias=True, exclude=["id"])
        await self.collection.insert_one(user_dict)
        
        created_doc = await self.collection.find_one({"user_id": user_id})
        logger.info("New OAuth user created", email=email, provider=oauth_provider)
        
        return UserModel(**created_doc)
