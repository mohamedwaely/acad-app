from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from controllers.admin_controller import add_admin_controller, get_admins_controller
from models.schemas import Admin, AdminDBBase, AdminResponse
from models.database import get_db
from services.auth_service import get_current_admin

router = APIRouter()

@router.post("/add-admin", response_model=AdminDBBase)
async def add_admin_route(
    admin_data: Admin,
    db: Session = Depends(get_db),
    cur_admin=Depends(get_current_admin)
):
    """Add a new admin role (requires degree-A admin).
    
    Args:
        admin_data: Admin data including username, email, password, and degree.
        db: Database session.
        cur_admin: Current authenticated admin role.
    
    Returns:
        AdminDBBase: The authenticated admin role.
    """
    return await add_admin_controller(admin_data, db=db, cur_admin=cur_admin)

@router.post("/register-admin", response_model=AdminDBBase)
async def register_admin(
    admin_data: Admin,
    db: Session = Depends(get_db),
    cur_admin=Depends(get_current_admin)
):
    """Register a new admin (requires degree-A admin).
    
    Args:
        admin_data: Admin data including username, email, password, and degree.
        db: Database session.
        cur_admin: Current authenticated admin user.
    
    Returns:
        AdminDBBase: The created admin user.
    """
    if cur_admin.degree != "A":
        raise HTTPException(status_code=403, detail="Only degree-A admins can register admins")
    return await add_admin_controller(admin_data, db=db, cur_admin=cur_admin)

@router.get("/admins/{degree}", response_model=list[AdminResponse])
@router.get("/admins/", response_model=list[AdminResponse])
async def get_admins_route(
    degree: str | None = None,
    db: Session = Depends(get_db),
    cur_admin=Depends(get_current_admin),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return")
):
    """Retrieve admins with optional degree filter and pagination.
    
    Args:
        degree: Optional admin degree filter ('A' or 'B').
        db: Database session.
        cur_admin: Current authenticated admin.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
    
    Returns:
        list[AdminResponse]: List of admins.
    """
    return await get_admins_controller(degree, db=db, cur_admin=cur_admin, skip=skip, limit=limit)