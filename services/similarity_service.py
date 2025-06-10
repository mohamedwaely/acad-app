import logging
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from models.entities import PreProjects
from models.schemas import CheckProject
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def calculate_similarity(project: CheckProject, projects: list[PreProjects]) -> list[tuple[int, float]]:
    """Calculate cosine similarity between a project and existing projects.
    
    Args:
        project: Project to compare.
        projects: List of existing projects.
    
    Returns:
        list[tuple[int, float]]: List of (index, similarity_score) tuples.
    
    Raises:
        HTTPException: If title or description is empty.
    """
    if not project.title or not project.description:
        raise HTTPException(status_code=400, detail="Title and description cannot be empty")
    proj_txt = f"{project.title} {project.description}"
    projs_txt = [f"{pro.title} {pro.description}" for pro in projects]
    if not projs_txt:
        return []
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([proj_txt] + projs_txt)
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        return [(i, score) for i, score in enumerate(similarity_matrix[0])]
    except Exception as e:
        logger.error(f"Similarity calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate similarity")

def check_similarity(project: CheckProject, db: Session) -> dict:
    """Check similarity of a project against existing pre-projects.
    
    Args:
        project: Project to check.
        db: Database session.
    
    Returns:
        dict: Response with similarity results or success message.
    
    Raises:
        HTTPException: If project addition fails.
    """
    cur_date = datetime.now()
    cur_month = cur_date.month
    cur_year = cur_date.year

    # Configurable year increment for project submission period
    submission_months = [int(m) for m in os.getenv('SUBMISSION_MONTHS', '10,11,12').split(",")]
    if cur_month in submission_months:
        cur_year += 1
    
    projects = db.query(PreProjects).filter(PreProjects.year == cur_year).all()

    if not projects:
        try:
            new_proj = PreProjects(
                title=project.title,
                description=project.description,
                year=cur_year
            )
            db.add(new_proj)
            db.commit()
            db.refresh(new_proj)
            return {"message": "Project added successfully", "similarity": "Your is the first project in the year"}
        except Exception as e:
            logger.error(f"Error adding project: {str(e)}")
            raise HTTPException(status_code=400, detail="Error in adding project")
    
    all_similarities = calculate_similarity(project, projects)
    similar_projects = [(i, score) for i, score in all_similarities if score > 0.5]

    if similar_projects:
        sim_projs = [
            {"title": projects[i].title, "similarity score": f"{score:.2f}"} for i, score in similar_projects
        ]
        return {
            "message": "There are projects similar to your idea due to DMU policy", 
            "similar projects": sim_projs
        }
    
    try:
        new_proj = PreProjects(
            title=project.title,
            description=project.description,
            year=cur_year
        )
        db.add(new_proj)
        db.commit()
        db.refresh(new_proj)
        all_projs = [
            {"title": projects[i].title, "similarity score": f"{score:.2f}"} for i, score in all_similarities
        ]
        return {
            "message": "Congrats, Your project added successfully",
            "similarity scores": all_projs,
        }
    except Exception as e:
        logger.error(f"Error adding project: {str(e)}")
        raise HTTPException(status_code=400, detail="Error in adding project")