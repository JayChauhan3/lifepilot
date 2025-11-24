from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _pre_hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

password = "StrongP@ss1"
pre_hashed = _pre_hash_password(password)
print(f"Pre-hashed length: {len(pre_hashed)}")
print(f"Pre-hashed value: {pre_hashed}")

try:
    hashed = pwd_context.hash(pre_hashed)
    print(f"Hashed: {hashed}")
except Exception as e:
    print(f"Error: {e}")

long_password = "A" * 100
pre_hashed_long = _pre_hash_password(long_password)
print(f"Long Pre-hashed length: {len(pre_hashed_long)}")
try:
    hashed_long = pwd_context.hash(pre_hashed_long)
    print(f"Hashed long: {hashed_long}")
except Exception as e:
    print(f"Error long: {e}")
