import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.entities import Project
from models.schemas import ProjectBase, ProjectsResponse

logger = logging.getLogger(__name__)

def upload_project(data: ProjectBase, uploader_username: str, db: Session) -> dict:
    """Upload a new project to the database.
    
    Args:
        data: Project data including title, description, tools, etc.
        uploader_username: Username of the uploader.
        db: Database session.
    
    Returns:
        dict: Success message.
    
    Raises:
        HTTPException: If project title exists or upload fails.
    """
    tools_str = " ".join(data.tools)
    if db.query(Project).filter(Project.title == data.title).first():
        raise HTTPException(status_code=400, detail="Project title already exists")
    proj = Project(
        uploader=uploader_username,
        title=data.title,
        description=data.description,
        tools=tools_str,
        supervisor=data.supervisor,
        year=data.year,
    )
    try:
        db.add(proj)
        db.commit()
        db.refresh(proj)
        return {"res": "Project uploaded successfully"}
    except Exception as e:
        logger.error(f"Failed to upload project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload project: {str(e)}")

def get_projects(title: str | None, db: Session, skip: int = 0, limit: int = 10) -> list[ProjectsResponse] | ProjectsResponse:
    """Retrieve projects with optional title filter and pagination.
    
    Args:
        title: Optional project title filter.
        db: Database session.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
    
    Returns:
        list[ProjectsResponse] or ProjectsResponse: List of projects or single project.
    
    Raises:
        HTTPException: If project not found or query fails.
    """
    try:
        query = db.query(Project)
        if title:
            project = query.filter(Project.title == title).first()
            if project is None:
                raise HTTPException(status_code=404, detail=f"Project with title '{title}' not found")
            return ProjectsResponse.model_validate(project)
        projects = query.offset(skip).limit(limit).all()
        return [ProjectsResponse.model_validate(p) for p in projects]
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Failed to get projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")