import json
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends
from loguru import logger

from src.models.order.schemas import CreateOrderSchemas, OrderIdSchemas
from src.models.user_session.task.tasks_cookie import get_or_create_user_session
from src.pika.config.rabbit_connection import rabbit_connection

router = APIRouter(prefix="/create_order_rabbit", tags=["RabbitMQ"])



@router.post("/")
async def create_order_rabbit(
        order: CreateOrderSchemas,
        cookie_id=Depends(get_or_create_user_session)
) -> OrderIdSchemas:
    task_id = str(uuid.uuid4())

    payload = order.model_dump()
    payload.update({
        'background_task_id': task_id,
        'session_uuid': cookie_id
    })

    await rabbit_connection.send_message(
        messages=payload
    )
    return OrderIdSchemas(id=task_id)
