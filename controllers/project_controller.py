import logging
from fastapi import Depends
from sqlalchemy.orm import Session
from models.schemas import ProjectBase, ProjectsResponse
from models.entities import Admin
from services.project_service import upload_project, get_projects
from services.auth_service import get_current_admin
from models.database import get_db

logger = logging.getLogger(__name__)

async def upload_projects(data: ProjectBase, cur_admin: Admin, db: Session) -> dict:
    """Upload a new project to the database.
    
    Args:
        data: Project data including title, description, tools, etc.
        cur_admin: Current authenticated admin.
        db: Database session.
    
    Returns:
        dict: Success message.
    """
    try:
        return upload_project(data, cur_admin.username, db)
    except Exception as e:
        logger.error(f"Error uploading project: {str(e)}")
        raise

async def get_projects_controller(
    title: str | None,
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> list[ProjectsResponse] | ProjectsResponse:
    """Retrieve projects with optional title filter and pagination.
    
    Args:
        title: Optional project title filter.
        db: Database session.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
    
    Returns:
        list[ProjectsResponse] or ProjectsResponse: List of projects or single project.
    """
    try:
        return get_projects(title, db, skip, limit)
    except Exception as e:
        logger.error(f"Error retrieving projects: {str(e)}")
        raise