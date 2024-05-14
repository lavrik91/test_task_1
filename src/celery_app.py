import asyncio

from celery import Celery, current_task
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from order.task_celery import process_create_order
from utils.extra_logger import cel_logger, logger
app_celery = Celery('tasks', broker='amqp://guest:guest@localhost:5672', backend='redis://localhost')

loop = asyncio.get_event_loop()

redis = aioredis.from_url("redis://localhost")
FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app_celery.task
def create_order_task(item_data):
    """
    Запуск Celery в терминале:
    celery -A celery_app:app_celery worker --loglevel=info --pool=solo

    Задача по созданию заказа и расчета цены доставки
    """
    try:
        task_id = current_task.request.id
        cel_logger.info(f'INFO CELERY Create background task[{task_id}]')
        logger.info(f'INFO CELERY Create background task[{task_id}]')

        item_data['celery_task_id'] = task_id

        return loop.run_until_complete(process_create_order(item_data))

    except Exception as e:
        cel_logger.error(f'ERROR Celery task crush: {e}. {task_id=}')
