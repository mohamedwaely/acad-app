from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from controllers.admin_controller import add_admin_controller, get_admins_controller, regiadmin
from models.schemas import Admin, AdminDBBase, AdminResponse
from models.database import get_db
from services.auth_service import get_current_admin

router = APIRouter()

@router.post("/add-admin", response_model=AdminDBBase)
async def add_admin_route(admin_data: Admin, db: Session = Depends(get_db)):
    return await add_admin_controller(admin_data, db=db)


@router.get("/admins/{degree}", response_model=list[AdminResponse])
@router.get("/admins/", response_model=list[AdminResponse])
async def get_admins_route(
    degree: str | None = None,
    db: Session = Depends(get_db),
    cur_admin=Depends(get_current_admin)
):
    return await get_admins_controller(degree, db=db, cur_admin=cur_admin)

@router.post("/register-admin", response_model=AdminDBBase)
async def register_master(admin_data: Admin, db: Session = Depends(get_db)):
    return regiadmin(admin_data, db=db)