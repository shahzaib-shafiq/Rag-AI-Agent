from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import FAQ, Ticket  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print(f"Starting {settings.app_name}")
    Base.metadata.create_all(bind=engine)
    yield
    print(f"Stopping {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "documentation": "/docs",
    }