import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio

from loguru import logger
import aio_pika
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.pika.router import message_router
from src.config import settings

PARALLEL_TASKS = 1

logger.add(
    "".join(
        [
            str(settings.ROOT_PATH),
            "/logs/",
            settings.LOGGING.file_rabbitmq.lower(),
            ".log",
        ]
    ),
    format=settings.LOGGING.format,
    rotation=settings.LOGGING.rotation,
    compression=settings.LOGGING.compression,
    level="INFO",
)

redis = aioredis.from_url(settings.REDIS_URL)
FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


async def main() -> None:
    connection = await aio_pika.connect_robust(settings.RABBIT_URL)

    queue_name = settings.RMQ_QUEUE

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=PARALLEL_TASKS)
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        logger.info("Starting RabbitMQ")

        await queue.consume(message_router)

        try:
            await asyncio.Future()
        finally:
            await connection.close()


if __name__ == '__main__':
    logger.info("Starting RabbitMQ")
    asyncio.run(main())
