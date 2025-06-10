import os
from datetime import timedelta, datetime
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv('SEC_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("SEC_KEY must be set and at least 32 characters long")

ALGORITHM = "HS256"
USER_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('USER_TOKEN_EXPIRE_MINUTES', '30'))
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ADMIN_TOKEN_EXPIRE_MINUTES', '60'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, is_admin: bool = False, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Payload data to encode.
        is_admin: Whether the token is for an admin user.
        expires_delta: Optional custom expiration time.
    
    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire_minutes = ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES if is_admin else USER_ACCESS_TOKEN_EXPIRE_MINUTES
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt