from fastapi import FastAPI
import uvicorn
from app import models
from app.db import engine
from app.routes import router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
models.Base.metadata.create_all(bind=engine)

# CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:8080", 
#         "https://*.vercel.app",
#         "https://*.netlify.app",
#         "*"  # Remove this in production
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {
        "message": "The Project is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }


app.include_router(router)

if __name__=="__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=5555)