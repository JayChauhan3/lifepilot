from pydantic_settings import BaseSettings
from typing import Optional
import structlog

logger = structlog.get_logger()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    MONGODB_URI: str
    
    # AI Services
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "lifepilot-memory"
    GEMINI_API_KEY: str
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "gemini"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    
    # Vector Database
    VECTOR_DB_PROVIDER: str = "pinecone"
    
    # LLM Configuration
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.0-flash-exp"
    
    # Server Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Authentication
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    JWT_SECRET_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

def get_settings() -> Settings:
    """Get validated settings"""
    try:
        settings = Settings()
        logger.info("Settings loaded and validated successfully")
        return settings
    except Exception as e:
        logger.error("Failed to load settings", error=str(e))
        raise

# Global settings instance
settings = get_settings()