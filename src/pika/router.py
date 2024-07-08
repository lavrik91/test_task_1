import json

from loguru import logger
from aio_pika.abc import AbstractIncomingMessage

from src.pika.task.create_order import create_order


async def message_router(message: AbstractIncomingMessage) -> None:
    logger.info(f"Данные поступающие в задачу: {message.body}")
    async with message.process():
        body = json.loads(message.body.decode())
        logger.info(f"Данные после декодинга: {body}")
        return await create_order(body)



