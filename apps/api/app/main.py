from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.observability import instrument_engine, metrics_response, observe_request
from app.db.base import Base
from app.db.session import engine
from app.modules.articles import models as article_models  # noqa: F401
from app.modules.auth.dependencies import DatabaseSession
from app.modules.friendships import models as friendship_models  # noqa: F401
from app.modules.posts import models as post_models  # noqa: F401
from app.modules.users import models as user_models  # noqa: F401

settings = get_settings()
configure_logging()
instrument_engine(engine)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(observe_request)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["operations"])
def readiness(db: DatabaseSession) -> dict[str, str]:
    db.execute(select(1))
    return {"status": "ready", "database": "reachable"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return metrics_response(engine)
