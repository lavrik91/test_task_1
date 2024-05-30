from fastapi import HTTPException, status, Request

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

    async def get_orders_for_user(self, request: Request, order_type, delivery_cost, page, page_size):
        cookie_id = request.cookies.get('session_id')

        if cookie_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orders not found")

        if order_type is not None:
            order_type = order_type.value

        res = await self.repo.get_orders_for_user(
            order_type=order_type,
            delivery_cost=delivery_cost,
            cookie_id=cookie_id,
            page=page,
            page_size=page_size
        )

        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orders not found")
        return res
