from typing import List, Annotated

from fastapi import APIRouter, Depends, Request, Query, status
from fastapi_cache.decorator import cache

from src.celery.celery_app import create_order_task
from src.services.order import OrderService
from src.tasks.tasks_cookie import get_or_create_user_session
from .dependencies import order_service, order_type_service
from .schemas import CreateOrderSchemas, OrderTypeSchemas, OrderSchemas, OrderTypeEnum, OrderIdSchemas
from src.utils.transaction import transaction

router = APIRouter()


@router.post('/create_order', status_code=status.HTTP_201_CREATED)
@transaction
async def create_order(
        order: Annotated[CreateOrderSchemas, Depends()],
        cookie_id=Depends(get_or_create_user_session)
):
    """Create order
    cookie_id:
        Checking for the presence of the user's session id on our site.
        If there is no id, then a session is created and the id is recorded to the user in a cookie
    """
    # регистрация посылок с использованием Celery and RabbitMQ
    order = create_order_task.delay(order.model_dump(), cookie_id)
    return OrderIdSchemas(id=order.id)


@router.get('/order_type_list', response_model=List[OrderTypeSchemas], status_code=status.HTTP_200_OK)
@cache(expire=None)
@transaction
async def get_types_order_list(
        service: Annotated[OrderService, Depends(order_type_service)]
):
    """Get all order types"""

    order_types = await service.get_order_types()
    return order_types


@router.get('/get_user_orders_list', response_model=list[OrderSchemas], status_code=status.HTTP_200_OK)
@transaction
async def get_orders_user_list(
        request: Request,
        service: Annotated[OrderService, Depends(order_service)],
        order_type: OrderTypeEnum = Query(default=None,
                                          description='Type of the order: Clothing, Electronics, Miscellaneous'),
        delivery_cost: bool = Query(default=None, description='Whether the cost is calculated or not'),
        page: int = 1,
        page_size: int = 10,
):
    """Get all user orders, with pagination and filtering by order type and shipping price"""

    orders = await service.get_orders_for_user(request, order_type, delivery_cost, page, page_size)
    return orders


@router.get('/{order_id}', response_model=OrderSchemas, status_code=status.HTTP_200_OK)
@cache(expire=120)
@transaction
async def get_order_by_id(
        order_id: Annotated[OrderIdSchemas, Depends()],
        service: Annotated[OrderService, Depends(order_service)]
):
    """Get order by id"""

    order = await service.get_order(order_id.id)
    return order
