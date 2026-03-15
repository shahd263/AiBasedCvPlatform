"""Application configuration."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database (sync for migrations/tools; async for app)
    DATABASE_URL: str = "postgresql://postgres:2003@localhost:5432/CvPlatform"
    ASYNC_DATABASE_URL: str | None = None  # defaults to postgresql+asyncpg://... if not set

    def get_async_database_url(self) -> str:
        if self.ASYNC_DATABASE_URL:
            return self.ASYNC_DATABASE_URL
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    GEMINI_API_KEY: str = "AIzaSyDrmLon5aF3bfCCKeMhJthq6vhu8neKCtU"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
