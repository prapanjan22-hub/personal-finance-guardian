from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import api_router
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    try:
        from app.data import models as data_models  # Import to register models
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

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
