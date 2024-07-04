from abc import ABC, abstractmethod
from typing import Generic, Type

from sqlalchemy import select, or_, update, Result
from fastapi import HTTPException
from starlette import status

from src.database.database import Session
from src.database.models import ConcreteTable


class AbstractRepository(ABC):
    @abstractmethod
    async def create(self, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def update(self, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def find_one(self, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def find_all(self):
        raise NotImplemented

    @abstractmethod
    async def get_orders_for_user(self, **kwargs):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository, Session, Generic[ConcreteTable]):
    """
    Repository class for interacting with SQLAlchemy models.

    Args:
        AbstractRepository: Abstract base class for repositories.
        Session: SQLAlchemy session for database operations.
        Generic[ConcreteTable]: Generic type for the SQLAlchemy model.

    Attributes:
        model (Type[ConcreteTable]): SQLAlchemy model type managed by this repository.
    """

    model: Type[ConcreteTable]

    def __init__(self):
        """
        Initializes the SQLAlchemyRepository instance.

        Raises:
            HTTPException: If the model attribute is missing.
        """
        super().__init__()

        if not self.model:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot initialize the class without model attribute"
            )

    async def create(self, payload: dict) -> ConcreteTable:
        """
        Creates a new object of type ConcreteTable using provided data.

        Args:
            payload (dict): Data dictionary for creating the object.

        Returns:
            ConcreteTable: Created object of type ConcreteTable.

        Raises:
            HTTPException: If there is a database error (status code 500).
        """
        try:
            schema = self.model(**payload)
            self._session.add(schema)
            await self._session.flush()
            await self._session.refresh(schema)
            return schema
        except self._ERRORS as e:
            print(f'ERROR {e}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    async def update(self, update_data: dict, id: str) -> str:
        """
        Updates data of an existing ConcreteTable object identified by id.

        Args:
            update_data (dict): Data dictionary with fields to update.
            id (str): Identifier of the object to update.

        Returns:
            str: Identifier of the updated object.

        Raises:
            HTTPException: If there is a database error (status code 500).
        """
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model.id)
        )
        result: Result = await self.execute(stmt)
        await self._session.flush()

        if not (_result := result.scalar_one_or_none()):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

        await self._session.commit()

        return _result

    async def find_one(self, id: str) -> ConcreteTable:
        """
        Finds a single ConcreteTable object by order_id or Celery task id.

        Args:
            order_id (str): Order identifier or Celery task id.

        Returns:
            ConcreteTable: Found ConcreteTable object.

        Raises:
            HTTPException: If no objects are found (status code 404).
        """
        query = (
            select(self.model)
            .where(or_(self.model.celery_task_id == id, self.model.id == id))
        )

        result: Result = await self.execute(query)

        if not (_result := result.scalar_one_or_none()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')

        return _result

    async def find_all(self) -> list[ConcreteTable]:
        """
        Retrieves all ConcreteTable objects.

        Returns:
            list[ConcreteTable]: List of all ConcreteTable objects.

        Raises:
            HTTPException: If no objects are found (status code 404).
        """
        query = select(self.model)
        result: Result = await self.execute(query)

        if not (_result := result.scalars().all()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        return _result

    async def get_orders_for_user(
            self,
            order_type: str | None,
            delivery_cost: bool | None,
            cookie_id: str,
            page: int,
            page_size: int
    ) -> list[ConcreteTable]:
        """
        Retrieves orders for a specific user with optional filters for order type and delivery cost.

        Args:
            order_type (str | None): Optional filter for order type.
            delivery_cost (bool | None): Optional filter for delivery cost presence.
            cookie_id (str): Unique identifier of the user.
            page (int): Page number for pagination.
            page_size (int): Number of items per page.

        Returns:
            list[ConcreteTable]: List of orders for the user with applied filters.

        Raises:
            HTTPException: If no orders are found (status code 404).
        """
        query = (
            select(self.model)
            .filter(self.model.session_uuid == cookie_id)
        )

        if order_type is not None:
            query = query.filter(self.model.order_type_name == order_type)

        if delivery_cost is not None:
            if delivery_cost:
                query = query.filter(self.model.delivery_cost != "Не рассчитана")
            else:
                query = query.filter(self.model.delivery_cost == "Не рассчитана")

        offset = (page - 1) * page_size
        limit = page_size
        query = query.offset(offset).limit(limit)

        result: Result = await self.execute(query)

        if not (_result := result.scalars().all()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        return _result
