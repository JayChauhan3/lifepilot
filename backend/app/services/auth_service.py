import structlog
from passlib.context import CryptContext
from typing import Optional
from app.core.database import get_database
from app.models import UserModel
from datetime import datetime
import uuid

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.collection_name = "users"
    
    @property
    def collection(self):
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized")
        return db[self.collection_name]
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
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
    
    async def get_user_by_user_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by user_id"""
        try:
            doc = await self.collection.find_one({"user_id": user_id})
            if doc:
                return UserModel(**doc)
            return None
        except Exception as e:
            logger.error("Failed to get user by user_id", error=str(e))
            return None
    
    async def register_user(self, email: str, password: str, full_name: Optional[str] = None) -> UserModel:
        """
        Register a new user with email and password
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            full_name: Optional full name
            
        Returns:
            Created UserModel
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        
        user = UserModel(
            user_id=user_id,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            is_active=True,
            is_verified=False
        )
        
        user_dict = user.model_dump(by_alias=True, exclude=["id"])
        await self.collection.insert_one(user_dict)
        
        created_doc = await self.collection.find_one({"user_id": user_id})
        logger.info("User registered", email=email, user_id=user_id)
        
        return UserModel(**created_doc)
    
    async def authenticate_user(self, email: str, password: str) -> UserModel:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            UserModel if authentication successful
            
        Raises:
            ValueError: With specific error message for different failure cases
        """
        user = await self.get_user_by_email(email)
        
        if not user:
            logger.warning("Authentication failed: user not found", email=email)
            raise ValueError("No account found with this email. Please sign up first.")
        
        if not user.password_hash:
            logger.warning("Authentication failed: no password set", email=email)
            raise ValueError("This account was created with Google. Please use 'Sign in with Google'.")
        
        if not self.verify_password(password, user.password_hash):
            logger.warning("Authentication failed: invalid password", email=email)
            raise ValueError("Incorrect password. Please try again.")
        
        if not user.is_active:
            logger.warning("Authentication failed: user inactive", email=email)
            raise ValueError("Your account has been deactivated. Please contact support.")
        
        logger.info("User authenticated", email=email, user_id=user.user_id)
        return user
