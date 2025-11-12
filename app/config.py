"""
Configuration - Optimized for Render with port 10000
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration - PORT 10000 for Render
    SECRET_KEY: str = os.getenv("SECRET_KEY", "quiz-solver-secret-key-2024")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", 10000))  # Default 10000
    
    # Browser Configuration - Optimized for speed
    BROWSER_TIMEOUT: int = 30000  # 30 seconds (reduced from 180)
    HEADLESS: bool = True
    
    # NO OPENAI - Prevents 429 rate limit errors
    OPENAI_API_KEY: Optional[str] = None  # Not used
    
    # Quiz Configuration - Fast timeouts
    MAX_RETRIES: int = 2  # Reduced from 3
    REQUEST_TIMEOUT: int = 20  # Reduced from 30
    DATA_TIMEOUT: int = 30  # 30s for data loading
    SOLVE_TIMEOUT: int = 45  # 45s for solving
    
    # Performance
    MAX_DATA_ROWS: int = 50000  # Limit dataset size
    MAX_RESULT_ROWS: int = 100  # Limit result size
    
    # Keep-alive (prevents 599 timeout)
    ENABLE_KEEPALIVE: bool = True
    KEEPALIVE_INTERVAL: int = 840  # 14 minutes (Render free tier sleeps at 15 min)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
