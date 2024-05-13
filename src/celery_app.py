import asyncio

from celery import Celery, current_task
from celery.utils.log import get_task_logger
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from order.task_celery import process_create_order
from utils.extra_logger import logger


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
        logger.info('INFO CELERY Create background task')
        task_id = current_task.request.id
        item_data['celery_task_id'] = task_id
        logger.info(f'{item_data=}')
        # return loop.run_until_complete(process_create_order(item_data))

    except Exception as e:
        logger.error(f'ERROR Celery task crush: {e}')