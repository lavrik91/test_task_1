import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.config import settings
from src.pika.config.rabbit_connection import rabbit_connection
from src.routers.order import router as router_order
from src.routers.order_type import router as router_type
from src.routers.order_create_RMQ import router as router_create_RMQ



logger.add(
    "".join(
        [
            str(settings.ROOT_PATH),
            "/logs/",
            settings.LOGGING.file.lower(),
            ".log",
        ]
    ),
    format=settings.LOGGING.format,
    rotation=settings.LOGGING.rotation,
    compression=settings.LOGGING.compression,
    level="INFO",
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    await rabbit_connection.connect()
    yield
    await rabbit_connection.disconnect()


app = FastAPI(title="Order App", lifespan=lifespan)

app.include_router(router_order, prefix="/api/v1")

app.include_router(router_type, prefix="/api/v1")

app.include_router(router_create_RMQ, prefix="/api/v1")

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)
