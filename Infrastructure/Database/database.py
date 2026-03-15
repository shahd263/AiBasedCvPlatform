"""Database connection and session management (async)."""
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from Core.config import settings
from Infrastructure.Database.base import Base
from Infrastructure.Database.models import UserModel, ResumeModel  # noqa: F401 - register models

# Async engine and session for the application
async_engine = create_async_engine(
    settings.get_async_database_url(),
    pool_pre_ping=True,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Sync engine (optional, for migrations or scripts)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_tables() -> None:
    """Create all database tables. Call on application startup."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
