from __future__ import annotations

from typing import Any

import httpx
import redis
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import engine

router = APIRouter()


def _dependency(status_value: str, detail: str | None = None) -> dict[str, str]:
    payload = {"status": status_value}
    if detail:
        payload["detail"] = detail
    return payload


def check_postgres() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return _dependency("ok")
    except SQLAlchemyError as exc:
        return _dependency("error", str(exc.__class__.__name__))


def check_redis() -> dict[str, str]:
    client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
    try:
        client.ping()
        return _dependency("ok")
    except redis.RedisError as exc:
        return _dependency("error", str(exc.__class__.__name__))
    finally:
        client.close()


def check_qdrant() -> dict[str, str]:
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get(f"{settings.qdrant_url}/healthz")
            response.raise_for_status()
        return _dependency("ok")
    except httpx.HTTPError as exc:
        return _dependency("error", str(exc.__class__.__name__))


def check_ollama() -> dict[str, str]:
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
        return _dependency("ok")
    except httpx.HTTPError as exc:
        return _dependency("error", str(exc.__class__.__name__))


@router.get("/health")
def health(response: Response) -> dict[str, Any]:
    dependencies = {
        "postgres": check_postgres(),
        "redis": check_redis(),
        "qdrant": check_qdrant(),
        "ollama": check_ollama(),
    }
    healthy = all(dependency["status"] == "ok" for dependency in dependencies.values())

    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "service": settings.project_name,
        "environment": settings.environment,
        "status": "ok" if healthy else "degraded",
        "dependencies": dependencies,
    }
