import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Rural Utility Analyzer"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkeywithoutenvfornow"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    # Database - Load from .env file
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017/utility_analyzer")
    
    # Weather API
    WEATHER_API_KEY: str = "bd5e378503939ddaee76f12ad7a97608"

    class Config:
        env_file = ".env"
        extra = "ignore" # Allow extra fields in .env

settings = Settings()
