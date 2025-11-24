from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
import structlog
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService, oauth
from app.core.jwt_utils import create_access_token, verify_token
from app.models import UserModel
from app.core.security import validate_password, validate_email

router = APIRouter()
logger = structlog.get_logger()
auth_service = AuthService()
oauth_service = OAuthService()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Request/Response models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserVerify(BaseModel):
    email: EmailStr
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Validate email format
        email_error = validate_email(user_data.email)
        if email_error:
            raise ValueError(email_error)

        # Validate password strength
        password_error = validate_password(user_data.password)
        if password_error:
            raise ValueError(password_error)

        user = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        logger.info("User registered successfully", email=user_data.email)
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=False  # Always false initially
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password"""
    try:
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.user_id})
        
        logger.info("User logged in", user_id=user.user_id)
        
        return Token(access_token=access_token, token_type="bearer")
    
    except ValueError as e:
        # Specific error from auth service
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/auth/verify", response_model=Token)
async def verify_email(verify_data: UserVerify):
    """Verify email address"""
    try:
        await auth_service.verify_email(verify_data.email, verify_data.code)
        
        # Get user to create token
        user = await auth_service.get_user_by_email(verify_data.email)
        access_token = create_access_token(data={"sub": user.user_id})
        
        return Token(access_token=access_token, token_type="bearer")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed"
        )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """Get current user information"""
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = await auth_service.get_user_by_user_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified
    )

# Google OAuth endpoints
@router.get("/auth/google/login")
async def google_login(request: Request):
    """Redirect to Google OAuth login"""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        email = user_info.get('email')
        oauth_id = user_info.get('sub')
        full_name = user_info.get('name')
        
        if not email or not oauth_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required user information"
            )
        
        # Create or update user
        user = await oauth_service.create_or_update_oauth_user(
            email=email,
            oauth_provider='google',
            oauth_id=oauth_id,
            full_name=full_name
        )
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.user_id})
        
        # Redirect to frontend with token
        frontend_url = "http://localhost:3000"  # TODO: Get from config
        return RedirectResponse(url=f"{frontend_url}/auth/callback?token={access_token}")
        
    except Exception as e:
        logger.error("Google OAuth callback failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )
