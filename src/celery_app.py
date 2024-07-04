import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio

from loguru import logger
from celery import Celery, current_task
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.config import settings
from src.worker.task_celery import process_create_order

app_celery = Celery('tasks', broker=settings.RABBIT_URL, backend=settings.REDIS_URL)

logger.remove()
logger.add(
    "".join(
        [
            str(settings.ROOT_PATH),
            "/logs/",
            settings.LOGGING.file_celery.lower(),
            ".log",
        ]
    ),
    format=settings.LOGGING.format,
    rotation=settings.LOGGING.rotation,
    compression=settings.LOGGING.compression,
    level="INFO",
)


loop = asyncio.get_event_loop()

redis = aioredis.from_url(settings.REDIS_URL)
FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app_celery.task(name='src.cel_app.create_order_task')
def create_order_task(payload, cookie_id):
    """
    Celery task for creating an order and calculating delivery cost.

    To start Celery in the terminal:
    celery -A celery_app:app_celery worker --loglevel=info --pool=solo

    Args:
        payload (dict): Data dictionary containing order details.
        cookie_id (str): User session ID used for associating the order with a specific user.

    Returns:
        Awaitable: Task result from process_create_order coroutine.

    Notes:
        This task processes the creation of an order asynchronously, assigning a unique task ID and session UUID.
        It updates the item_data dictionary with 'celery_task_id' and 'session_uuid' before calling process_create_order.
    """

    task_id = current_task.request.id
    logger.info(f'INFO CELERY Create background task[{task_id}]')

    payload.update({
        'celery_task_id': task_id,
        'session_uuid': cookie_id
    })

    return loop.run_until_complete(process_create_order(payload))
