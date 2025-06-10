import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.entities import Admin, User
from models.schemas import Admin, AdminResponse
from utils.security import get_hashed_password
from services.auth_service import get_user, get_admin

logger = logging.getLogger(__name__)

def add_admin(admin_data: Admin, current_admin_email: str, current_admin_degree: str, db: Session) -> Admin:
    """Add a new admin to the database.
    
    Args:
        admin_data: Admin data including username, email, password, and degree.
        current_admin_email: Email of the admin performing the action.
        current_admin_degree: Degree of the admin performing the action.
        db: Database session.
    
    Returns:
        Admin: The created admin entity.
    
    Raises:
        HTTPException: If the current admin lacks permission or email exists.
    """
    if current_admin_degree != 'A':
        raise HTTPException(status_code=403, detail="Only admins with degree A can add other admins")
    
    existing_user = get_user(db, email=admin_data.email)
    existing_admin = get_admin(db, email=admin_data.email)
    if existing_user or existing_admin:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = get_hashed_password(admin_data.password)
    
    new_admin = Admin(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=hashed_password,
        degree=admin_data.degree,
        added_by=current_admin_email
    )
    
    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        return new_admin
    except Exception as e:
        logger.error(f"Failed to add admin: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add admin: {str(e)}")

def get_admins(degree: str | None, current_admin_degree: str, db: Session, skip: int = 0, limit: int = 10) -> list[AdminResponse]:
    """Retrieve a list of admins with optional degree filter and pagination.
    
    Args:
        degree: Optional degree filter ('A' or 'B').
        current_admin_degree: Degree of the admin performing the action.
        db: Database session.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
    
    Returns:
        list[AdminResponse]: List of admin response models.
    
    Raises:
        HTTPException: If the current admin lacks permission or query fails.
    """
    if current_admin_degree != 'A':
        raise HTTPException(status_code=403, detail="Only admins with degree A can view other admins")
    try:
        query = db.query(Admin)
        if degree:
            query = query.filter(Admin.degree == degree)
        admins = query.offset(skip).limit(limit).all()
        return [AdminResponse.model_validate(admin) for admin in admins]
    except Exception as e:
        logger.error(f"Failed to get admins: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve admins: {str(e)}")