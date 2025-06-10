from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from controllers.project_controller import upload_projects, get_projects_controller
from models.schemas import ProjectBase, ProjectsResponse
from models.database import get_db
from services.auth_service import get_current_admin

router = APIRouter()

@router.post("/upload-projects")
async def upload_projects_route(
    data: ProjectBase,
    db: Session = Depends(get_db),
    cur_admin=Depends(get_current_admin)
):
    """Upload a new project (requires admin access).
    
    Args:
        data: Project data including title, description, tools, and other data.
        db: Database session.
        cur_admin: Current authenticated admin.
    
    Returns:
        dict: Success message.
    """
    return await upload_projects(data, cur_admin, db)

@router.get("/projects/{title}", response_model=ProjectsResponse)
@router.get("/projects", response_model=list[ProjectsResponse])
async def get_projects_route(
    title: str | None = None,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return")
):
    """Retrieve projects with optional title filter and pagination.
    
    Args:
        title: Optional project title filter.
        db: Database session.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
    
    Returns:
        list[ProjectsResponse] or ProjectsResponse: List of projects or single project.
    """
    return await get_projects_controller(title, db, skip, limit)