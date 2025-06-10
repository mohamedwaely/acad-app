import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models.entities import Base
from models.database import engine
from routes.auth_routes import router as auth_router
from routes.project_routes import router as project_router
from routes.admin_routes import router as admin_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Management API",
    description="FastAPI application for project management and AI chat",
    version="1.0.0"
)

# Configure CORS
# frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[frontend_url],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["Authorization", "Content-Type"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check the health status of the API."""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Project Management API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")
    raise

# Include routers
app.include_router(auth_router, prefix="/v1", tags=["Authentication"])
app.include_router(project_router, prefix="/v1", tags=["Projects"])
app.include_router(admin_router, prefix="/v1", tags=["Admin"])

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)