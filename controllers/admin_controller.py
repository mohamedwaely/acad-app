import logging
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models.schemas import Admin, AdminDBBase, AdminResponse
from services.admin_service import add_admin, get_admins
from services.auth_service import get_current_admin
from models.database import get_db

logger = logging.getLogger(__name__)

async def add_admin_controller(
    admin_data: Admin,
    db: Session = Depends(get_db),
    cur_admin=Depends(get_current_admin)
) -> AdminDBBase:

    if not hasattr(cur_admin, 'email') or not hasattr(cur_admin, 'degree'):
        logger.error("Invalid admin data received")
        raise HTTPException(status_code=500, detail="Invalid admin data")
    try:
        return add_admin(admin_data, cur_admin.email, cur_admin.degree, db)
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error adding admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add admin")

async def get_admins_controller(
    degree: str | None = None,
    db: Session = Depends(get_db),
    cur_admin=Depends(get_current_admin),
    skip: int = 0,
    limit: int = 10
) -> list[AdminResponse]:

    try:
        return get_admins(degree, cur_admin.degree, db, skip, limit)
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving admins: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve admins")