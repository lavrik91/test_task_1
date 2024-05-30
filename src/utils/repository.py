from abc import ABC, abstractmethod

from sqlalchemy import select, or_, insert, update

from src.database import Session
from src.order.schemas import OrderSchemas
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
    session = None

    async def create(self, data: dict) -> str:
        try:
            async with self.session() as db:
                stmt = (
                    insert(self.model)
                    .values(**data)
                    .returning(self.model.id)
                )
                res = await db.execute(stmt)
                await db.commit()
            return res.scalar_one_or_none()

        except Exception as e:
            cel_logger.error(f'Error when creating an object in the database: {e}')
            return None

    async def update(self, update_data: dict, id: str) -> str:
        try:
            async with self.session() as db:
                stmt = (
                    update(self.model)
                    .where(self.model.id == id)
                    .values(**update_data)
                    .returning(self.model.id)
                )
                res = await db.execute(stmt)
                await db.commit()
            return res.scalars().one()
        except Exception as e:
            cel_logger.error(f'Error updating an object in the database: {e}')
            return None

    async def find_one(self, order_id: str):
        """Метод для таблицы Order.
         Осуществляет поиск заказа по id
        """
        try:
            async with self.session() as db:
                query = (
                    select(self.model)
                    .where(or_(self.model.celery_task_id == order_id, self.model.id == order_id))
                )

                res = await db.execute(query)
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
            async with self.session() as db:
                # вывод всех типов посылок
                query = select(self.model)
                res = await db.execute(query)
                res_dto = [row[0].to_read_model() for row in res.all()]
            return res_dto
        except Exception as e:
            cel_logger.error(f'Error when searching for order types in the database: {e}')
            return None

    async def get_orders_for_user(
            self,
            order_type: str | None,
            delivery_cost: bool | None,
            cookie_id: str,
            page: int,
            page_size: int
    ):
        try:
            async with Session() as session:
                try:
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

                    orders = await session.execute(query)

                    return orders.scalars().all()
                except Exception as e:
                    logger.error(f'{e}')
        except Exception as e:
            logger.error(f'Ошибка при поиске заказов пользователя в базе данных: {e}')
            return None
