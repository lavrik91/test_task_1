import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import asyncio

from loguru import logger
from celery import Celery, current_task
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.config import settings
from src.celery.task.task_celery import process_create_order


app_celery = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

logger.remove()
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
    enqueue=True,
)

loop = asyncio.get_event_loop()

redis = aioredis.from_url(settings.RADIS_URL)
FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app_celery.task
def create_order_task(item_data, cookie_id):
    """
    Запуск Celery в терминале:
    celery -A celery_app:app_celery worker --loglevel=info --pool=solo

    Задача по созданию заказа и расчета цены доставки
    """
    try:
        task_id = current_task.request.id
        logger.info(f'INFO CELERY Create background task[{task_id}]')
        logger.complete()

        item_data['celery_task_id'] = task_id
        item_data['session_uuid'] = cookie_id

        return loop.run_until_complete(process_create_order(item_data))

    except Exception as e:
        logger.error(f'ERROR Celery task crush: {e}. {task_id=}')
