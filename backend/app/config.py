"""Application configuration."""
import warnings
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # App
    APP_NAME: str = "Predictive Risk & Resource Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./predictive_pm.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # API
    API_V1_STR: str = "/api/v1"

    # LLM
    OPENAI_API_KEY: Optional[str] = None
    
    # WebSocket
    WS_URL: str = "ws://localhost:8001"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

if not settings.OPENAI_API_KEY:
    warnings.warn(
        "OPENAI_API_KEY is not set; LLM-powered features will fail until provided.",
        stacklevel=1,
    )
