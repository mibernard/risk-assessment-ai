"""
Configuration management using environment variables.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./dev.db"
    
    # IBM watsonx.ai
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    # Application
    log_level: str = "INFO"
    debug: bool = False
    
    # Token budget
    token_budget_usd: float = 250.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings

