"""Application configuration."""
from __future__ import annotations

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    # load_dotenv()
    # Database (sync for migrations/tools; async for app)
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ASYNC_DATABASE_URL: str | None = None  # defaults to postgresql+asyncpg://... if not set

    def get_async_database_url(self) -> str:
        if self.ASYNC_DATABASE_URL:
            return self.ASYNC_DATABASE_URL
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"

load_dotenv()
settings = Settings()
