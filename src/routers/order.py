from typing import List, Annotated

from fastapi import APIRouter, Depends, Request, Query, status
from fastapi_cache.decorator import cache

from src.celery_app import create_order_task
from src.services.order import OrderService
from src.models.user_session.task.tasks_cookie import get_or_create_user_session
from src.models.order.dependencies import order_service
from src.models.order.schemas import (
    CreateOrderSchemas,
    OrderSchemas,
    OrderIdSchemas
)
from src.models.order_types.schemas import OrderTypeEnum
from src.database.transaction import transaction

router = APIRouter(prefix="/order", tags=["Order"])


@router.post('/create_order', status_code=status.HTTP_201_CREATED)
@transaction
async def create_order(
        # order: Annotated[CreateOrderSchemas, Depends()],
        order: CreateOrderSchemas,
        cookie_id=Depends(get_or_create_user_session)
) -> OrderIdSchemas:
    """
    Endpoint to create a new order by using Celery.

    Args:
        order (CreateOrderSchema): Data schema for creating an order.
        cookie_id (str): User session ID stored in a cookie, or a new session ID if absent.

    Returns:
        OrderIdSchema: ID of the created order.
    """

    # регистрация посылок с использованием Celery and RabbitMQ
    order = create_order_task.delay(order.model_dump(), cookie_id)
    return OrderIdSchemas(id=order.id)


@router.get('/get_user_orders_list', response_model=list[OrderSchemas], status_code=status.HTTP_200_OK)
@transaction
async def get_orders_user_list(
        request: Request,
        service: Annotated[OrderService, Depends(order_service)],
        order_type: Annotated[
            OrderTypeEnum | None,
            Query(description='Type of the order: Clothing, Electronics, Miscellaneous')
        ] = None,
        delivery_cost: Annotated[
            bool | None,
            Query(description='Whether the cost is calculated or not')
        ] = None,
        page: int = 1,
        page_size: int = 10,
):
    """
    Endpoint to retrieve all orders for a user, with optional filters by order type and delivery cost.

    Args:
        request (Request): FastAPI Request object.
        service (OrderService): Service dependency for retrieving user orders.
        order_type (OrderTypeEnum, optional): Optional filter for order type.
        delivery_cost (bool, optional): Optional filter for delivery cost presence.
        page (int, optional): Page number for pagination.
        page_size (int, optional): Number of orders per page.

    Returns:
        List[OrderSchema]: List of user orders filtered by the specified parameters.

    Raises:
        HTTPException: If no orders are found (status code 404).
    """

    orders = await service.get_orders_for_user(request, order_type, delivery_cost, page, page_size)
    return orders


@router.get('/{order_id}', response_model=OrderSchemas, status_code=status.HTTP_200_OK)
@cache(expire=120)
@transaction
async def get_order_by_id(
        order_id: Annotated[OrderIdSchemas, Depends()],
        service: Annotated[OrderService, Depends(order_service)]
):
    """
    Endpoint to retrieve an order by its ID.

    Args:
        order_id (str): ID of the order to retrieve.
        service (OrderService): Service dependency for retrieving orders.

    Returns:
        OrderSchema: Schema of the retrieved order.

    Raises:
        HTTPException: If the specified order is not found (status code 404).
    """

    order = await service.get_order(order_id.id)
    return order
