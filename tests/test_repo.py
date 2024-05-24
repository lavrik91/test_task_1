import pytest
from decimal import Decimal
from uuid import uuid4

from conftest import async_session_maker
from src.order.models import OrderType, Order, UserSession
from src.order.schemas import OrderTypeSchemas, OrderSchemas
from src.utils.repository import SQLAlchemyRepository


@pytest.fixture(scope='module')
def uuid_id():
    return str(uuid4())


# @pytest.fixture(autouse=True)
# async def del_orders():
#     async with async_session_maker() as session:
#         await session.execute(text("DELETE FROM orders;"))
#         await session.execute(text("DELETE FROM user_sessions;"))
#         await session.execute(text("DELETE FROM order_types;"))
#         await session.commit()


@pytest.fixture(scope='module')
def repo():
    repo = SQLAlchemyRepository()
    repo.model = Order
    repo.session = async_session_maker

    return repo


@pytest.fixture(scope='module')
def repo_type():
    repo = SQLAlchemyRepository()
    repo.model = OrderType
    repo.session = async_session_maker

    return repo


@pytest.fixture(scope='module', autouse=True)
async def create_user_session_and_order_type(uuid_id):
    order_type = [OrderType(id=2, name='Electronics'), UserSession(id=3, session_id=uuid_id)]
    orders = [
        Order(id=uuid_id, name='test', weight=12, cost=2, session_uuid=uuid_id, celery_task_id='fsdh12213bhghasg21',
              order_type_name='Electronics'),
        Order(id='123123dsada2e31c3212', name='test_1', weight=1231, cost=12, session_uuid=uuid_id,
              celery_task_id='123123c1312csdffsd', order_type_name='Clothing')
    ]

    async with async_session_maker() as session:
        session.add_all(order_type)
        session.add_all(orders)
        await session.commit()



@pytest.mark.usefixtures('create_user_session_and_order_type')
class TestRepo:
    async def test_create(self, repo, uuid_id):
        order_data = {
            'id': '123123vfsdafsd',
            'name': 'test_2',
            'weight': 123,
            'cost': 4,
            'session_uuid': uuid_id,
            'celery_task_id': 'asghdfy321egahs',
            'order_type_name': 'Clothing'
        }
        order_id = await repo.create(order_data)
        assert order_id == order_data['id']

    async def test_update(self, repo, uuid_id):
        update_data = {'name': 'qwer', 'delivery_cost': '1213.12'}
        order_id = await repo.update(update_data, uuid_id)
        assert order_id == uuid_id

    async def test_find_one(self, repo, uuid_id):
        res = await repo.find_one(uuid_id)
        assert res.model_dump() == {
            'cost': Decimal('2.00'),
            'delivery_cost': '1213.12',
            'id': uuid_id,
            'name': 'qwer',
            'order_type_name': 'Electronics',
            'weight': Decimal('12.000')
        }

    async def test_find_all(self, repo_type):
        res = await repo_type.find_all()
        assert len(res) == 2
        assert res == [OrderTypeSchemas(id=1, name='Clothing'), OrderTypeSchemas(id=2, name='Electronics')]

    async def test_get_orders_for_user(self, repo, uuid_id):
        res = await repo.get_orders_for_user(order_type=None, delivery_cost=None, cookie_id=uuid_id, page=1,
                                             page_size=10)
        orders = [OrderSchemas.model_validate(i) for i in res]

        assert len(orders) == 3
        assert orders[-1].id == uuid_id
        assert orders[0].name == 'test_1'
