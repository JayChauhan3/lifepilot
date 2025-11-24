import pytest
from app.core.security import validate_password, get_password_hash, verify_password, validate_email

def test_validate_password_valid():
    assert validate_password("StrongP@ss1") is None

def test_validate_password_too_short():
    assert validate_password("Short1!") == "Password must be at least 8 characters long"

def test_validate_password_too_long():
    long_pass = "A" * 129 + "1!"
    assert validate_password(long_pass) == "Password must be at most 128 characters long"

def test_validate_password_no_upper():
    assert validate_password("weakp@ss1") == "Password must contain at least one uppercase letter"

def test_validate_password_no_lower():
    assert validate_password("WEAKP@SS1") == "Password must contain at least one lowercase letter"

def test_validate_password_no_number():
    assert validate_password("WeakP@ss") == "Password must contain at least one number"

def test_validate_password_no_special():
    assert validate_password("WeakPass1") == "Password must contain at least one special character"

def test_hashing_verification():
    password = "StrongP@ss1"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("WrongP@ss1", hashed)

def test_hashing_long_password():
    # Test password longer than 72 bytes (bcrypt limit)
    long_password = "A" * 100 + "StrongP@ss1"
    hashed = get_password_hash(long_password)
    assert verify_password(long_password, hashed)
    assert not verify_password(long_password + "a", hashed)

def test_validate_email_valid():
    assert validate_email("test@example.com") is None
    assert validate_email("user.name+tag@sub.domain.co.uk") is None

def test_validate_email_invalid():
    assert validate_email("invalid-email") is not None
    assert validate_email("test@") is not None
    assert validate_email("@example.com") is not None
    assert validate_email("test@example") is not None  # Missing TLD often considered invalid by default or strict checks
