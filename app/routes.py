from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from app import auth, models, schemas, security
from app.db import get_db
from app.models import User, Admin
import os
from controllers.check_similarity import check_similarity

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

router = APIRouter()

@router.post("/v1/upload-project")
async def upload_projects(data: schemas.ProjectBase, cur_admin: schemas.AdminDB = Depends(auth.getCurrentAdmin), db: Session = Depends(get_db)):
    tools_str = " ".join(data.tools)

    proj = models.Project(
        uploader=cur_admin.username,
        title=data.title,
        description=data.description,
        tools=tools_str,
        supervisor=data.supervisor,
        year=data.year,
    )
    if db.query(models.Project).filter(models.Project.title == data.title).first():
        raise HTTPException(status_code=500, detail=f"Project title already exists")
    try:
        db.add(proj)
        db.commit()
        db.refresh(proj)
        return {"res": "Project uploaded successfully"}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=f"Failed to upload project: {str(e)}")

@router.post("/v1/register", response_model=schemas.UserDBBase)
async def register(user: schemas.User, db: Session = Depends(get_db)):
    db_val = auth.getUser(db, email=user.email)  # Check by email
    if db_val:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = security.getHashedPassword(user.password)
    db_user = models.User(
        **user.dict(exclude={'password'}),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/v1/token", response_model=schemas.Token)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Check if the user exists in the users table
    user = auth.getUser(db, email=login_data.email)  # Use email instead of username
    is_admin = False
    
    if not user:
        # If not found in users, check if the user is an admin
        user = auth.getAdmin(db, email=login_data.email)  # Use email instead of username
        if user:
            is_admin = True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Verify the password
    if not security.pwd_context.verify(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with appropriate expiration time
    access_token = security.create_access_token(
        data={"sub": user.email},  # Use email as the subject (sub) in JWT
        is_admin=is_admin
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/v1/add-admin", response_model=schemas.AdminDBBase)
async def add_admin(admin_data: schemas.Admin, cur_admin: schemas.AdminDB = Depends(auth.getCurrentAdmin), db: Session = Depends(get_db)):
    
    # Check if the current admin has degree 'A'
    if cur_admin.degree != 'A':
        raise HTTPException(status_code=403, detail="Only admins with degree A can add other admins")
    
    # Check if the email already exists in users or admins
    existing_user = auth.getUser(db, email=admin_data.email)
    existing_admin = auth.getAdmin(db, email=admin_data.email)
    if existing_user or existing_admin:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Hash the password
    hashed_password = security.getHashedPassword(admin_data.password)
    
    # Create the new admin
    new_admin = models.Admin(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=hashed_password,
        degree=admin_data.degree,
        added_by=cur_admin.email
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

from typing import Optional
@router.get("/v1/admins/{degree}", response_model=list[schemas.AdminResponse])
@router.get("/v1/admins/", response_model=list[schemas.AdminResponse])
async def get_admins(degree: Optional[str] = None, cur_admin: schemas.AdminDB = Depends(auth.getCurrentAdmin), db: Session = Depends(get_db)):
    # Check if the current admin has degree 'A'
    if cur_admin.degree != 'A':
        raise HTTPException(status_code=403, detail="Only admins with degree A can view other admins")
    try: 
        query = db.query(
            models.Admin.id,
            models.Admin.username,
            models.Admin.email,
            models.Admin.degree,
            models.Admin.added_by
        )
        if degree is None:
            admins=query.all()
        else:
            admins=query.filter(models.Admin.degree == degree).all()

        return admins
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get admins: {str(e)}")

@router.get("/v1/projects/{title}", response_model=schemas.ProjectsResponse)
@router.get("/v1/projects", response_model=list[schemas.ProjectsResponse])
async def get_projects(title: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(
            models.Project.id,
            models.Project.title,
            models.Project.description,
            models.Project.tools,
            models.Project.supervisor,
            models.Project.year
        )

        if title is None:
            # Return all projects
            projects = query.all()
            return projects
        else:
            # Return a single project by title
            project = query.filter(models.Project.title == title).first()
            if project is None:
                raise HTTPException(status_code=404, detail=f"Project with title '{title}' not found")
            return project

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")


@router.post("/v1/check-similarity")
async def check_proj_similarity(project: schemas.checkProject, db: Session = Depends(get_db)):
    return check_similarity(project, db)

