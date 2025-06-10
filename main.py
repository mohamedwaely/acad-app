from fastapi import FastAPI
import uvicorn
from models.entities import Base
from models.database import engine
from routes.auth_routes import router as auth_router
from routes.project_routes import router as project_router
from routes.admin_routes import router as admin_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Project Management API",
    description="FastAPI application for project management and AI chat",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check first (before DB operations)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {
        "message": "Project Management API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Create tables if they don't exist
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Database table creation warning: {e}")


# Include routers
app.include_router(auth_router, prefix="/v1", tags=["Authentication"])
app.include_router(project_router, prefix="/v1", tags=["Projects"])
app.include_router(admin_router, prefix="/v1", tags=["Admin"])

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
