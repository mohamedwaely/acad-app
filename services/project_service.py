from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.entities import Project
from models.schemas import ProjectBase


def upload_project(data: ProjectBase, uploader_username: str, db: Session) -> dict:

    if db.query(Project).filter(Project.title == data.title).first():
        raise HTTPException(status_code=500, detail="Project title already exists")

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
        raise HTTPException(status_code=500, detail=f"Failed to upload project: {str(e)}")

def get_projects(title: str | None, db: Session) -> list[Project] | Project:
    try:
        query = db.query(
            Project.id,
            Project.title,
            Project.description,
            Project.tools,
            Project.supervisor,
            Project.year
        )

        if title is None:
            return query.all()
        else:
            project = query.filter(Project.title == title).first()
            if project is None:
                raise HTTPException(status_code=404, detail=f"Project with title '{title}' not found")
            return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")