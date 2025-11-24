import structlog
from passlib.context import CryptContext
from typing import Optional
from app.core.database import get_database
from app.models import UserModel
from datetime import datetime, timedelta
import uuid
import secrets

logger = structlog.get_logger()

# Password hashing
from app.core.security import get_password_hash, verify_password

# Email service
from app.core.email_service import email_service

class AuthService:
    def __init__(self):
        self.collection_name = "users"
        self.pending_collection_name = "pending_registrations"
    
    @property
    def collection(self):
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized")
        return db[self.collection_name]

    @property
    def pending_collection(self):
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized")
        return db[self.pending_collection_name]
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return get_password_hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return verify_password(plain_password, hashed_password)
    
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
        # Directly create an active, verified user for development
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password and create user record
        password_hash = self.hash_password(password)
        user_id = str(uuid.uuid4())
        user_dict = {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "password_hash": password_hash,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
        }
        # Insert into main collection
        await self.collection.insert_one(user_dict)
        logger.info("Dev user created and activated", email=email, user_id=user_id)
        
        return UserModel(
            user_id=user_id,
            email=email,
            full_name=full_name,
            is_active=True,
            is_verified=True,
        )

    async def verify_email(self, email: str, code: str) -> bool:
        """
        Verify email with code
        """
        # Check pending collection first
        pending_user = await self.pending_collection.find_one({"email": email})
        
        if not pending_user:
            # Check if already verified in main collection
            user = await self.get_user_by_email(email)
            if user and user.is_verified:
                return True
            raise ValueError("Invalid verification request")
            
        if pending_user.get("verification_token") != code:
            raise ValueError("Invalid verification code")
            
        if pending_user.get("verification_token_expires_at") < datetime.utcnow():
            raise ValueError("Verification code expired")
            
        # Move to main collection
        user = UserModel(
            user_id=pending_user["user_id"],
            email=pending_user["email"],
            full_name=pending_user.get("full_name"),
            password_hash=pending_user["password_hash"],
            is_active=True,
            is_verified=True,
            verification_token=None,
            verification_token_expires_at=None
        )
        
        user_dict = user.model_dump(by_alias=True, exclude=["id"])
        await self.collection.insert_one(user_dict)
        
        # Remove from pending
        await self.pending_collection.delete_one({"email": email})
        
        logger.info("User verified and moved to main collection", email=email)
        return True
    
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
        
        if not user.is_verified:
            logger.warning("Authentication failed: user not verified", email=email)
            raise ValueError("Please verify your email address first.")

        if not user.is_active:
            logger.warning("Authentication failed: user inactive", email=email)
            raise ValueError("Your account has been deactivated. Please contact support.")
        
        logger.info("User authenticated", email=email, user_id=user.user_id)
        return user
