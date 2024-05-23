import pytest
import time
from uuid import uuid4

from conftest import async_session_maker
from src.order.models import OrderType, Order, UserSession
from src.order.schemas import OrderTypeSchemas, OrderSchemas, UserSessionSchemas
from src.order.dependencies import order_service, order_type_service
from src.utils.repository import SQLAlchemyRepository


@pytest.fixture(scope='class')
def uuid_id():
    return str(uuid4())


@pytest.fixture(scope='session')
def repo():
    class TestRepository(SQLAlchemyRepository):
        model = Order

    return TestRepository()


@pytest.fixture(scope='class', autouse=True)
async def create_user_session_and_order_type(uuid_id):
    order_type = [OrderType(id=1, name='Clothing'), UserSession(id=1, session_id=uuid_id)]
    order = Order(id=uuid_id, name='test', weight=12, cost=2, session_uuid=uuid_id, celery_task_id=uuid_id, order_type_name='Clothing')

    async with async_session_maker() as session:
        session.add_all(order_type)
        session.add(order)
        await session.commit()


@pytest.mark.usefixtures('create_user_session_and_order_type')
class TestRepo:
    async def test_create(self, repo, uuid_id):
        order_data = {
            'id': '123123vfsdafsd',
            'name': 'test_1',
            'weight': 123,
            'cost': 4,
            'session_uuid': uuid_id,
            'celery_task_id': 'asghdfy321egahs',
            'order_type_name': 'Clothing'
        }
        order_id = await repo.create(order_data)
        assert order_id == order_data['id']

    async def test_update(self, repo, uuid_id):
        update_data = {'name': 'qwer', 'delivery_cost': '1223.12'}
        res = await repo.update(update_data, uuid_id)
        assert res == uuid_id

    async def test_find_one(self, repo, uuid_id):
        res = await repo.find_one(uuid_id)
        assert res == {}

    # async def test_find_all(self, repo, uuid_id):
    #     res = await service.get_orders_for_user(uuid_id, order_type=None, delivery_cost=None, )
    #     assert res == {}

    # async def test_get_orders_for_user(self, repo, uuid_id):
    #     ...
