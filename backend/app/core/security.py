import re
import hashlib
from typing import Optional
import bcrypt
from email_validator import validate_email as validate_email_lib, EmailNotValidError

def validate_password(password: str) -> Optional[str]:
    """
    Validate password strength.
    
    Rules:
    - Minimum 8 characters
    - Maximum 128 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    
    Args:
        password: The password to validate
        
    Returns:
        Error message string if invalid, None if valid
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return "Password must be at most 128 characters long"
        
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
        
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
        
    if not re.search(r"\d", password):
        return "Password must contain at least one number"
        
    if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return "Password must contain at least one special character"
        
    return None

def validate_email(email: str) -> Optional[str]:
    """
    Validate email address format and deliverability.
    
    Args:
        email: The email address to validate
        
    Returns:
        Error message string if invalid, None if valid
    """
    try:
        validate_email_lib(email, check_deliverability=False)
        return None
    except EmailNotValidError as e:
        return str(e)

def _pre_hash_password(password: str) -> str:
    """
    Pre-hash password with SHA-256 to handle arbitrary lengths and avoid
    bcrypt's 72-byte limit.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt with SHA-256 pre-hashing.
    """
    pre_hashed = _pre_hash_password(password)
    # bcrypt.hashpw requires bytes, returns bytes
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pre_hashed.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using SHA-256 pre-hashing.
    """
    pre_hashed = _pre_hash_password(plain_password)
    try:
        return bcrypt.checkpw(pre_hashed.encode(), hashed_password.encode())
    except ValueError:
        # Handle invalid hash format
        return False
