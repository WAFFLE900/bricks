from __future__ import annotations

import logging
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _describe_database_target(database_url: str) -> str:
    normalized = database_url
    if normalized.startswith("postgresql+psycopg://"):
        normalized = normalized.replace("postgresql+psycopg://", "postgresql://", 1)

    parsed = urlsplit(normalized)
    host = parsed.hostname or "unknown-host"
    port = parsed.port or 5432
    db_name = parsed.path.lstrip("/") or "unknown-db"
    return f"{host}:{port}/{db_name}"


def create_app() -> FastAPI:
    settings = get_settings()
    logger.info("Database target: %s", _describe_database_target(settings.database_url))
    application = FastAPI(title=settings.app_name)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()

