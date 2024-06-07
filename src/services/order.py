from fastapi import HTTPException, status, Request

from src.order.schemas import OrderSchemas, OrderTypeSchemas
from src.utils.repository import AbstractRepository
from src.order.models import *


class OrderService:
    def __init__(self, repo: AbstractRepository):
        self.repo: AbstractRepository = repo()

    async def create_order(self, data: dict) -> str:
        """Create order.

        :param data: dict - a dictionary with the data needed to create an order

        :return: str - order ID
        """

        res = await self.repo.create(data)
        return res

    async def update_order(self, data: dict, order_id: str) -> str:
        """Update order

        :param data: dict - a dictionary with the data needed to create an order
        :param order_id: str - order ID

        :return: str - ID order
        """

        res = await self.repo.update(data, order_id)
        return res

    async def get_order(self, order_id: str) -> OrderSchemas:
        """Search for a parcel by ID

        :param order_id: str - order ID

        :return: Order - order object
        """

        res = await self.repo.find_one(order_id)
        return res

    async def get_order_types(self) -> list[OrderTypeSchemas]:
        """A list of all the types of packages presented"""

        res = await self.repo.find_all()
        return res

    async def get_orders_for_user(
            self,
            request: Request,
            order_type,
            delivery_cost,
            page,
            page_size
    ) -> list[OrderSchemas]:
        cookie_id = request.cookies.get('session_id')

        if cookie_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        if order_type is not None:
            order_type = order_type.value

        res = await self.repo.get_orders_for_user(
            order_type=order_type,
            delivery_cost=delivery_cost,
            cookie_id=cookie_id,
            page=page,
            page_size=page_size
        )
        return res
