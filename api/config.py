"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_key: str = Field(
        default="dev_test_key_12345",
        description="API key for authentication"
    )

    # Database
    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection string (optional for Phase 1)"
    )

    # Redis Cache
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection string"
    )

    # Application
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode"
    )

    # CORS
    allowed_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )

    # Data Directory
    data_dir: str = Field(
        default="data",
        description="Directory containing CSV data files"
    )

    # Cache TTL (Time To Live)
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache expiration time in seconds (default: 1 hour)"
    )

    # Existing API Keys (from original .env)
    anthropic_api_key: Optional[str] = Field(
        default=None,
        alias="ANTHROPIC_API_KEY"
    )
    odds_api_key: Optional[str] = Field(
        default=None,
        alias="ODDS_API_KEY"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
