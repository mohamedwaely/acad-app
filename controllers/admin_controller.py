from fastapi import Depends
from sqlalchemy.orm import Session
from models.schemas import Admin, AdminDBBase, AdminResponse
from services.admin_service import add_admin, get_admins
from services.auth_service import get_user, get_admin
from models.database import get_db
from models.entities import Admin as AdminEntity
from utils.security import get_hashed_password
from fastapi import HTTPException

def regiadmin(admin_data: Admin, db: Session) -> AdminEntity:
    existing_user = get_user(db, email=admin_data.email)
    existing_admin = get_admin(db, email=admin_data.email)
    if existing_user or existing_admin:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = get_hashed_password(admin_data.password)
    
    new_admin = AdminEntity(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=hashed_password,
        degree="A",
        added_by="System"
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

async def add_admin_controller(
    admin_data: Admin,
    cur_admin: AdminEntity,  # This is now the actual admin object, not a Depends
    db: Session
) -> AdminDBBase:
    return add_admin(admin_data, cur_admin.email, cur_admin.degree, db)

async def get_admins_controller(
    degree: str | None,
    cur_admin: AdminEntity,  # This is now the actual admin object, not a Depends
    db: Session
) -> list[AdminResponse]:
    return get_admins(degree, cur_admin.degree, db)
