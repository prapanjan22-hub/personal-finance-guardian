from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import api_router
from app.core.database import engine, Base
from app.data import models as data_models  # Import to register models

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
