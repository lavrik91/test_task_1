from abc import ABC, abstractmethod

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, or_, insert, update

from src.database import Session
from src.order.schemas import OrderTypeEnum, OrderSchemas
from .extra_logger import logger, cel_logger


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


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def create(self, data: dict) -> str:
        try:
            async with Session() as session:
                stmt = (
                    insert(self.model)
                    .values(**data)
                    .returning(self.model.id)
                )
                res = await session.execute(stmt)
                await session.commit()
                return res.scalars().one()
        except Exception as e:
            cel_logger.error(f'Error when creating an object in the database: {e}')

    async def update(self, update_data: dict, id: str) -> str:
        try:
            async with Session() as session:
                stmt = (
                    update(self.model)
                    .where(self.model.id == id)
                    .values(**update_data)
                    .returning(self.model.id)
                )
                res = await session.execute(stmt)
                await session.commit()
                return res
        except Exception as e:
            cel_logger.error(f'Error updating an object in the database: {e}')

    async def find_one(self, order_id: str):
        """Метод для таблицы Order.
         Осуществляет поиск заказа по id
        """
        try:
            async with Session() as session:
                query = (
                    select(self.model)
                    .where(or_(self.model.celery_task_id == str(order_id.id), self.model.id == str(order_id.id)))
                )

                res = await session.execute(query)
                res = res.scalars().first()

                if res is not None:
                    res = OrderSchemas.model_validate(res)
                return res
        except Exception as e:
            cel_logger.error(f'Error when searching by object id in the database: {e}')

    async def find_all(self):
        """Метод для таблицы OrderType.
         Выводит все типы заказов
        """
        try:
            async with Session() as session:
                # вывод всех типов посылок
                query = select(self.model)
                res = await session.execute(query)
                res_dto = [row[0].to_read_model() for row in res.all()]
                return res_dto
        except Exception as e:
            cel_logger.error(f'Error when searching for order types in the database: {e}')

    async def get_orders_for_user(
            self,
            order_type: OrderTypeEnum,
            delivery_cost: bool,
            cookie_id
    ):
        """Метод для таблицы Order.
        Список заказов пользователя с пагинацией и фильтрацией по типу заказа и выставлению цены доставки,
        по дефолту выводит все заказы пользователя.
        """
        try:
            async with Session() as session:
                query = (
                    select(self.model)
                    .filter(self.model.session_uuid == cookie_id)
                )

                # фильтрация по типу посылки
                if order_type is not None:
                    query = query.filter(self.model.order_type_name == order_type.value)

                # фильтрация по наличию цены за доставку
                if delivery_cost is not None:
                    if delivery_cost:
                        query = query.filter(self.model.delivery_cost != "Не рассчитана")
                    else:
                        query = query.filter(self.model.delivery_cost == "Не рассчитана")

                # пагинация результата поиска с разбивкой на страницы и количество заказов на одной страницы
                paginated_result = await paginate(session, query)
                return paginated_result
        except Exception as e:
            logger.error(f'Error when searching for user orders in the database: {e}')
