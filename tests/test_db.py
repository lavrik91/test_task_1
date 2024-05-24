from decimal import Decimal
from uuid import uuid4

from sqlalchemy import insert, select

from conftest import async_session_maker
from src.order.models import OrderType, Order, UserSession
from src.order.schemas import OrderTypeSchemas, OrderSchemas, UserSessionSchemas


class TestDB:
    async def test_create_order_type(self):
        async with async_session_maker() as session:
            stmt = insert(OrderType).values(id=1, name='Clothing')
            await session.execute(stmt)
            await session.commit()

            query = select(OrderType)
            res = await session.execute(query)
            res = OrderTypeSchemas.model_validate(res.scalar())
            assert res.model_dump() == {'id': 1, 'name': 'Clothing'}

    async def test_create_user_session(self):
        async with async_session_maker() as session:
            uuid_id = str(uuid4())
            await session.execute(insert(UserSession).values(id=1, session_id=uuid_id))
            await session.commit()

            query = select(UserSession)
            res = await session.execute(query)
            res = UserSessionSchemas.model_validate(res.scalar())
            assert res.model_dump() == {'id': 1, 'session_id': uuid_id}

    async def test_create_order(self):
        async with async_session_maker() as session:
            uuid_id = str(uuid4())
            await session.execute(insert(UserSession).values(id=2, session_id=uuid_id))
            stmt = (
                insert(Order)
                .values(id=uuid_id, name='test', weight=12,
                        cost=2, session_uuid=uuid_id,
                        celery_task_id=uuid_id,
                        order_type_name='Clothing')
            )
            await session.execute(stmt)
            await session.commit()

            query = select(Order)
            res = await session.execute(query)
            res = OrderSchemas.model_validate(res.scalar())
            assert res.model_dump() == {
                'cost': Decimal('2.00'), 'delivery_cost': 'Не рассчитана',
                'id': uuid_id, 'name': 'test',
                'order_type_name': 'Clothing', 'weight': Decimal('12.000')
            }
