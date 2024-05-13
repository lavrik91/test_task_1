from typing import List, Annotated

from fastapi import APIRouter, Depends, Request, Query, status
from fastapi_cache.decorator import cache
from fastapi_pagination import Page, add_pagination

from .dependencies import order_service, order_type_service
from .schemas import CreateOrderSchemas, OrderTypeSchemas, OrderSchemas, OrderTypeEnum, OrderIdSchemas
from .tasks import get_or_create_user_session
from services.order import OrderService


router = APIRouter()


@router.post('/create_order', status_code=status.HTTP_201_CREATED, response_model=OrderIdSchemas)
async def create_order(
        order: Annotated[CreateOrderSchemas, Depends()],
        service: Annotated[OrderService, Depends(order_service)],
        cookie_id=Depends(get_or_create_user_session)
):
    """Оформление заказа

    cookie_id:
        Проверка наличия id сессии пользователя на нашем сайте.
        Если id нет, то создается сессии и id записывается пользователю в cookie
    """
    # регистрация посылок с использованием Celery and RabbitMQ
    order_id = await service.create_order(order, cookie_id)

    return order_id


@router.get('/order_types', response_model=List[OrderTypeSchemas])
@cache(expire=None)
async def list_order_types(
        service: Annotated[OrderService, Depends(order_type_service)]
):
    """Список всех представленных типов посылок"""
    order_types = await service.get_order_types()
    return order_types


@router.get('/get_list_my_orders', response_model=Page[OrderSchemas])
async def get_list_my_order(
        request: Request,
        service: Annotated[OrderService, Depends(order_service)],
        order_type: OrderTypeEnum = Query(default=None,
                                          description='Type of the order: Clothing, Electronics, Miscellaneous'),
        delivery_cost: bool = Query(default=None, description='Whether the cost is calculated or not')
):
    """Список заказов пользователя по cookie_id с пагинацией и фильтрацией по типу заказа и выставлению цены доставки,
    по дефолту выводит все заказы пользователя.
    """
    orders = await service.get_orders_for_user(request, order_type, delivery_cost)
    return orders


add_pagination(router)


@router.get('/{order_id}', response_model=OrderSchemas)
@cache(expire=120)
async def get_order_list_by_id(
        order_id: Annotated[OrderIdSchemas, Depends()],
        service: Annotated[OrderService, Depends(order_service)]
):
    """Поиск посылки по Id"""
    order = await service.get_order(order_id)
    return order



