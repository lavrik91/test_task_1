from abc import ABC, abstractmethod
from uuid import uuid4

from sqlalchemy import select
from fastapi_pagination.ext.sqlalchemy import paginate

from database import async_session_maker
from celery_app import create_order_task
from order.schemas import CreateOrderSchemas, OrderTypeEnum, OrderSchemas, OrderIdSchemas
from order.models import Order


class AbstractRepository(ABC):
    @abstractmethod
    async def find_all(self):
        raise NotImplemented

    @abstractmethod
    async def find_one(self, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def add_order(self, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def get_orders_for_user(self, **kwargs):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def find_all(self):
        """Метод для таблицы OrderType.
         Выводит все типы заказов
        """
        async with async_session_maker() as session:
            # вывод всех типов посылок
            stmt = select(self.model)
            res = await session.execute(stmt)
            res_dto = [row[0].to_read_model() for row in res.all()]
            return res_dto

    async def find_one(self, order_id: str):
        """Метод для таблицы Order.
         Осуществляет поиск заказа по id
        """
        async with async_session_maker() as session:
            stmt = (
                select(self.model)
                .where(self.model.id == order_id)
            )

            res = await session.execute(stmt)
            res = res.scalars().first()
            res_dto = OrderSchemas.model_validate(res)
            return res_dto

    async def add_order(self, data: CreateOrderSchemas, cookie_id: str):
        """Метод для таблицы Order.
         Создает запись в таблице с использованием Celery and RabbitMQ
        """
        order_id = str(uuid4())
        data['id'] = order_id
        data['session_uuid'] = cookie_id

        # регистрация посылок с использованием Celery and RabbitMQ
        create_order_task.delay(data)
        res = OrderIdSchemas(id=order_id)
        return res

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
        async with async_session_maker() as session:
            stmt = select(self.model).filter(self.model.session_uuid == cookie_id)

            # фильтрация по типу посылки
            if order_type is not None:
                stmt = stmt.filter(self.model.order_type_name == order_type.value)

            # фильтрация по наличию цены за доставку
            if delivery_cost is not None:
                if delivery_cost:
                    stmt = stmt.filter(self.model.delivery_cost != "Не рассчитана")
                else:
                    stmt = stmt.filter(self.model.delivery_cost == "Не рассчитана")

            # пагинация результата поиска с разбивкой на страницы и количество заказов на одной страницы
            paginated_result = await paginate(session, stmt)
            return paginated_result
