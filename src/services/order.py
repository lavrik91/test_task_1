from fastapi import HTTPException, status, Request

from src.database.repository import AbstractRepository
from src.database.models import *


class OrderService:
    """Service class for managing orders."""

    def __init__(self, repo: AbstractRepository):
        """
        Initialize OrderService with a repository.

        Args:
            repo (AbstractRepository): Repository implementing database operations.
        """
        self.repo: AbstractRepository = repo()

    async def create_order(self, payload: dict) -> Order:
        """
        Create a new order based on provided data.

        Args:
            payload (dict): A dictionary with the data needed to create an order.

        Returns:
            Order: Created order object.

        Raises:
            HTTPException: If there is a database error (status code 500).
        """

        res = await self.repo.create(payload)
        return res

    async def update_order(self, payload: dict, order_id: str) -> str:
        """
        Update an existing order identified by order_id with new data.

        Args:
            payload (dict): A dictionary with the data needed to update an order.
            order_id (str): Identifier of the order to update.

        Returns:
            str: Identifier of the updated order.

        Raises:
            HTTPException: If there is a database error (status code 500).
        """

        res = await self.repo.update(payload, order_id)
        return res

    async def get_order(self, order_id: str) -> Order:
        """
        Retrieve an order by its unique order_id.

        Args:
            order_id (str): Identifier of the order to retrieve.

        Returns:
            Order: Retrieved order object.

        Raises:
            HTTPException: If the specified order is not found (status code 404).
        """

        res = await self.repo.find_one(order_id)
        return res

    async def get_orders_for_user(
            self,
            request: Request,
            order_type,
            delivery_cost,
            page,
            page_size
    ) -> list[Order]:
        """
        Retrieve orders for a specific user based on filters like order type and delivery cost.

        Args:
            request (Request): FastAPI request object containing cookies.
            order_type (str | None): Optional filter for order type.
            delivery_cost (bool | None): Optional filter for delivery cost presence.
            page (int): Page number for pagination.
            page_size (int): Number of items per page.

        Returns:
            list[Order]: List of orders for the user with applied filters.

        Raises:
            HTTPException: If user session ID is not found (status code 404).
        """
        cookie_id = request.cookies.get('session_id')

        if cookie_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You have not created any orders")

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
