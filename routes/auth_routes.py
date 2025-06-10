from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from controllers.auth_controller import register, login
from models.schemas import User, UserDBBase, Token, LoginRequest
from models.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserDBBase)
async def register_route(user: User, db: Session = Depends(get_db)):
    """Register a new user.
    
    Args:
        user: User data including username, email, and password.
        db: Database session.
    
    Returns:
        UserDBBase: The created user.
    """
    return await register(user, db)

@router.post("/token", response_model=Token)
async def login_route(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user or admin and return a JWT token.
    
    Args:
        login_data: Login credentials (email and password).
        db: Database session.
    
    Returns:
        Token: JWT token and token type.
    """
    return await login(login_data, db)