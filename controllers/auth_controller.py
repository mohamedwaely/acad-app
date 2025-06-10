import logging
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.schemas import User, UserDBBase, Token, LoginRequest
from models.entities import User as UserEntity
from models.entities import Admin as AdminEntity
from services.auth_service import get_user, get_admin
from utils.security import verify_password, create_access_token, get_hashed_password
from models.database import get_db

logger = logging.getLogger(__name__)

async def register(user: User, db: Session) -> UserDBBase:
    """Register a new user.
    
    Args:
        user: User data including username, email, and password.
        db: Database session.
    
    Returns:
        UserDBBase: The created user.
    
    Raises:
        HTTPException: If email already exists.
    """
    db_val = get_user(db, email=user.email)
    if db_val:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = get_hashed_password(user.password)
    db_user = UserEntity(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register user")

async def login(login_data: LoginRequest, db: Session) -> Token:
    """Authenticate a user or admin and return a JWT token.
    
    Args:
        login_data: Login credentials (email and password).
        db: Database session.
    
    Returns:
        Token: JWT token and token type.
    
    Raises:
        HTTPException: If credentials are invalid.
    """
    user = get_user(db, email=login_data.email)
    is_admin = False
    
    if not user:
        user = get_admin(db, email=login_data.email)
        if user:
            is_admin = True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email},
        is_admin=is_admin
    )
    return {"access_token": access_token, "token_type": "bearer"}