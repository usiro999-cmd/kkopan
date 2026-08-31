from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from redis.asyncio import Redis

from satdrone_common.config import get_settings


def create_app(service_name: str, version: str = "0.1.0") -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logging.basicConfig(
            level=settings.log_level,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        app.state.redis = Redis.from_url(settings.redis_url)
        yield
        await app.state.redis.aclose()

    app = FastAPI(
        title=f"SatDrone {service_name}",
        version=version,
        lifespan=lifespan,
    )

    @app.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok", "service": service_name}

    @app.get("/health/ready", tags=["health"])
    async def ready() -> dict[str, str]:
        await app.state.redis.ping()
        return {"status": "ready", "service": service_name}

    return app

