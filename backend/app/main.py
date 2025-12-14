from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import api_router
from app.core.database import engine, Base

# Create tables on startup (for now)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "active", 
        "system": settings.PROJECT_NAME, 
        "role": "guardian",
        "structure": "three_brains"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
