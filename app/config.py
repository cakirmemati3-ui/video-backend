"""
Configuration settings for Video Downloader Pro
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "Video Downloader Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    
    # Download Settings
    MAX_DOWNLOAD_SIZE_MB: int = 500
    DOWNLOAD_TIMEOUT_SECONDS: int = 300
    TEMP_DOWNLOAD_DIR: str = "./downloads"
    
    # Redis (Optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Create necessary directories
os.makedirs(settings.TEMP_DOWNLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
