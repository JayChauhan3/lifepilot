from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import structlog
import os

logger = structlog.get_logger()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data to encode (should include 'sub' for user_id)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("JWT token created", user_id=data.get("sub"))
    
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            return None
            
        return payload
        
    except JWTError as e:
        logger.error("JWT verification failed", error=str(e))
        return None

def decode_token(token: str) -> Optional[str]:
    """
    Decode token and extract user_id
    
    Args:
        token: JWT token string
        
    Returns:
        user_id or None if invalid
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
