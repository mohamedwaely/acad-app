import logging
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Union
from models.entities import User, Admin
from models.schemas import TokenData
from utils.security import SECRET_KEY, ALGORITHM
from models.database import get_db

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/token")

def get_user(db: Session, email: str) -> User:
    """Retrieve a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_admin(db: Session, email: str) -> Admin:
    """Retrieve an admin by email."""
    return db.query(Admin).filter(Admin.email == email).first()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Union[User, Admin]:
    """Retrieve the current user (user or admin) from a JWT token.
    
    Args:
        token: JWT token from Authorization header.
        db: Database session.
    
    Returns:
        Union[User, Admin]: The authenticated user or admin entity.
    
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        logger.debug(f"Decoded email: {email}")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
        
    admin = get_admin(db, email=token_data.email)
    if admin:
        return admin
        
    user = get_user(db, email=token_data.email)
    if user is None:
        logger.error(f"No user or admin found for email: {token_data.email}")
        raise credentials_exception
    return user

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    """Retrieve the current admin from a JWT token.
    
    Args:
        token: JWT token from Authorization header.
        db: Database session.
    
    Returns:
        Admin: The authenticated admin entity.
    
    Raises:
        HTTPException: If token is invalid or user is not an admin.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        logger.debug(f"Decoded email: {email}")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
        
    admin = get_admin(db, email=token_data.email)
    if not admin:
        logger.error(f"No admin found for email: {token_data.email}")
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    return admin