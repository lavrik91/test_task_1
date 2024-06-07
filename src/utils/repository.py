from abc import ABC, abstractmethod
from typing import Generic, Type

from loguru import logger
from sqlalchemy import select, or_, update, Result
from fastapi import HTTPException
from starlette import status

from src.database import Session
from src.order.models import ConcreteTable


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

    model: Type[ConcreteTable]

    def __init__(self):
        super().__init__()

        if not self.model:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Can not initiate the class without model attribute"
            )

    async def create(self, payload: dict) -> str:
        try:
            schema = self.model(**payload)
            self._session.add(schema)
            await self._session.flush()
            await self._session.refresh(schema)
            return schema.id
        except self._ERRORS:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    async def update(self, update_data: dict, id: str) -> str:
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

    async def find_one(self, order_id: str) -> ConcreteTable:
        """Метод для таблицы Order.
         Осуществляет поиск заказа по id
        """

        query = (
            select(self.model)
            .where(or_(self.model.celery_task_id == order_id, self.model.id == order_id))
        )

        result: Result = await self.execute(query)

        if not (_result := result.scalar_one_or_none()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')

        return _result

    async def find_all(self) -> list[ConcreteTable]:
        """Метод для таблицы OrderType.
         Выводит все типы заказов
        """

        # вывод всех типов посылок
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
        query = (
            select(self.model)
            .filter(self.model.session_uuid == cookie_id)
        )

        # фильтрация по типу посылки
        if order_type is not None:
            query = query.filter(self.model.order_type_name == order_type)

        # фильтрация по наличию цены за доставку
        if delivery_cost is not None:
            if delivery_cost:
                query = query.filter(self.model.delivery_cost != "Не рассчитана")
            else:
                query = query.filter(self.model.delivery_cost == "Не рассчитана")

        # Вычисляем смещение и лимит для страницы
        offset = (page - 1) * page_size
        limit = page_size

        # Применяем смещение и лимит
        query = query.offset(offset).limit(limit)

        result: Result = await self.execute(query)

        if not (_result := result.scalars().all()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        return _result
