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
from src.routers.order import router as router_order
from src.routers.order_type import router as router_type


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

app = FastAPI(
    title="Order App"
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app.include_router(
    router_order,
    prefix="/order",
    tags=["Order"]
)
app.include_router(
    router_type,
    prefix="/type",
    tags=["Type"]
)


origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)
