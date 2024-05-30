import pytest
from decimal import Decimal

from sqlalchemy import select, delete

from conftest import async_session_maker
from src.order.models import OrderType, Order, UserSession
from src.order.schemas import OrderTypeSchemas
from src.utils.repository import SQLAlchemyRepository


@pytest.fixture(scope='module', autouse=True)
async def empty_orders():
    async with async_session_maker() as session:
        stmt_order = delete(Order)
        stmt_order_type = delete(OrderType)
        stmt_user_session = delete(UserSession)

        await session.execute(stmt_order)
        await session.execute(stmt_order_type)
        await session.execute(stmt_user_session)
        await session.commit()

        query_2 = select(Order)
        result_2 = await session.execute(query_2)
        assert result_2.scalars().all() == []

        order_type = [OrderType(id=2, name='Electronics'),
                      UserSession(id=3, session_id='5ed1d2cf-e404-4f07-82df-5cd5834af8e4')]
        orders = [
            Order(id='ryutwevyutr3t4234', name='test', weight=12, cost=2,
                  session_uuid='5ed1d2cf-e404-4f07-82df-5cd5834af8e4',
                  celery_task_id='fsdh12213bhghasg212',
                  order_type_name='Electronics'),
            Order(id='67345vcwdfh3r4', name='test_1', weight=1231, cost=12,
                  session_uuid='5ed1d2cf-e404-4f07-82df-5cd5834af8e4',
                  celery_task_id='123123c1312csdffsd2', order_type_name='Electronics')
        ]

        session.add_all(order_type)
        session.add_all(orders)
        await session.commit()


@pytest.fixture(scope='class')
def repo():
    repo = SQLAlchemyRepository()
    repo.model = Order
    repo.session = async_session_maker

    return repo


@pytest.fixture(scope='class')
def repo_type():
    repo = SQLAlchemyRepository()
    repo.model = OrderType
    repo.session = async_session_maker

    return repo


@pytest.mark.usefixtures('empty_orders')
class TestRepo:
    @pytest.mark.anyio
    async def test_create(self, repo):
        order_data = {
            'id': '123123vfsdafsd',
            'name': 'test_2',
            'weight': 123,
            'cost': 4,
            'session_uuid': '5ed1d2cf-e404-4f07-82df-5cd5834af8e4',
            'celery_task_id': 'asghdfy321egahs',
            'order_type_name': 'Electronics'
        }
        order_id = await repo.create(order_data)
        assert order_id == order_data['id']

    @pytest.mark.anyio
    async def test_update(self, repo):
        update_data = {'name': 'qwer', 'delivery_cost': '1213.12'}
        order_id = await repo.update(update_data, id='ryutwevyutr3t4234')
        assert order_id == 'ryutwevyutr3t4234'

    @pytest.mark.anyio
    async def test_find_one(self, repo):
        res = await repo.find_one(order_id='67345vcwdfh3r4')
        assert res.model_dump() == {
            'cost': Decimal('12.00'),
            'delivery_cost': 'Не рассчитана',
            'id': '67345vcwdfh3r4',
            'name': 'test_1',
            'order_type_name': 'Electronics',
            'weight': Decimal('1231.000')
        }

    @pytest.mark.anyio
    async def test_find_all(self, repo_type):
        res = await repo_type.find_all()
        assert len(res) == 1
        assert res == [OrderTypeSchemas(id=2, name='Electronics')]

    @pytest.mark.anyio
    async def test_get_orders_for_user(self, repo):
        res = await repo.get_orders_for_user(order_type=None, delivery_cost=None,
                                             cookie_id='5ed1d2cf-e404-4f07-82df-5cd5834af8e4',
                                             page=1,
                                             page_size=10)
        # orders = [OrderSchemas.model_validate(i) for i in res]
        assert res == None
