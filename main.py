"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes.auth import router as auth_router
from api.routes.resume import router as resume_router
from api.routes.aiBased import router as aiBased_router
from Infrastructure.Database.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    await create_tables()
    yield


app = FastAPI(title="AI-based CV Platform", lifespan=lifespan)

app.include_router(auth_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(aiBased_router, prefix="/api")
