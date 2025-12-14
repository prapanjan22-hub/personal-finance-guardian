from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Personal Finance Guardian"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # Using generic default for now, compliant with docker-compose default usually
    DATABASE_URL: str = "postgresql://user:password@localhost/finance_guardian"
    
    # API Keys (To be filled by user later)
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
