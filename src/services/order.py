from fastapi import HTTPException, status, Request

from src.order.schemas import OrderTypeEnum
from src.utils.repository import AbstractRepository


class OrderService:
    def __init__(self, repo: AbstractRepository):
        self.repo: AbstractRepository = repo()

    async def create_order(self, data: dict) -> str:
        res = await self.repo.create(data)
        return res

    async def update_order(self, data: dict, order_id: str) -> str:
        res = await self.repo.update(data, order_id)
        return res

    async def get_order(self, order_id: str):
        """Поиск посылки по Id"""
        res = await self.repo.find_one(order_id)
        if res is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return res

    async def get_order_types(self):
        """Список всех представленных типов посылок"""
        res = await self.repo.find_all()

        if res is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Order types not created")
        return res

    async def get_orders_for_user(self, request: Request, order_type: OrderTypeEnum, delivery_cost: bool) -> dict:
        """Список заказов пользователя по cookie_id с пагинацией и фильтрацией по типу заказа и выставлению цены доставки,
            по дефолту выводит все заказы пользователя.
        """
        cookie_id = request.cookies.get('session_id')

        if cookie_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orders not found")

        res = await self.repo.get_orders_for_user(order_type, delivery_cost, cookie_id)

        if not res.items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orders not found")

        return res.dict()
