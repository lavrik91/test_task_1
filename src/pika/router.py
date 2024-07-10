import json

from aio_pika.abc import AbstractIncomingMessage

from src.pika.task.create_order import create_order


async def message_router(message: AbstractIncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body.decode())
        return await create_order(body)



