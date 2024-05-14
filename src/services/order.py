from fastapi import HTTPException, status, Request

from utils.repository import AbstractRepository
from order.schemas import CreateOrderSchemas, OrderTypeEnum


class OrderService:
    def __init__(self, repo: AbstractRepository):
        self.repo: AbstractRepository = repo()

    async def get_order_types(self):
        """Список всех представленных типов посылок"""
        res = await self.repo.find_all()

        if res is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Order types not created")
        return res

    async def get_order(self, order_id: str):
        """Поиск посылки по Id"""
        res = await self.repo.find_one(order_id)
        if res is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return res

    async def create_order(self, data: CreateOrderSchemas, cookie_id: str) -> str:
        """Оформление заказа"""
        res_id = await self.repo.add_order(data.model_dump(), cookie_id)
        return res_id

    async def get_orders_for_user(self, request: Request, order_type: OrderTypeEnum, delivery_cost: bool) -> dict:
        """Список заказов пользователя по cookie_id с пагинацией и фильтрацией по типу заказа и выставлению цены доставки,
            по дефолту выводит все заказы пользователя.
        """
        cookie_id = request.cookies.get('session_id')

        if cookie_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orders not found")

        res = await self.repo.get_orders_for_user(order_type, delivery_cost, cookie_id)

        if not res.items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found")

        return res.dict()
