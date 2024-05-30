import uuid

import pytest
from unittest.mock import patch, Mock
from httpx import AsyncClient
from sqlalchemy import delete

from conftest import async_session_maker
from src.order.models import Order, UserSession, OrderType


@pytest.fixture(scope='class', autouse=True)
async def empty_orders():
    async with async_session_maker() as session:
        stmt_order = delete(Order)
        stmt_order_type = delete(OrderType)
        stmt_user_session = delete(UserSession)

        await session.execute(stmt_order)
        await session.execute(stmt_order_type)
        await session.execute(stmt_user_session)
        await session.commit()

        order_type = [OrderType(id=1, name='Clothing'), UserSession(id=4, session_id='uuid_id_session_2')]
        orders = [
            Order(id='34527623tcb72t', name='test', weight=12, cost=2, session_uuid='uuid_id_session_2',
                  celery_task_id='fsdh12213bhghasg21',
                  order_type_name='Clothing'),
            Order(id='123123dsada2e31c3212', name='test_1', weight=1231, cost=12, session_uuid='uuid_id_session_2',
                  celery_task_id='123123c1312csdffsd', order_type_name='Clothing')
        ]

        session.add_all(order_type)
        session.add_all(orders)
        await session.commit()


@pytest.fixture
def mock_celery_task():
    fake_uuid = str(uuid.uuid4())
    with patch('src.order.routers.create_order_task.delay', return_value=Mock(id=fake_uuid)):
        yield fake_uuid


@pytest.mark.usefixtures('empty_orders')
class TestAPI:
    async def test_get_user_orders_list(self, ac: AsyncClient):
        cookies = {'session_id': 'uuid_id_session_2'}
        response = await ac.get('/order/get_user_orders_list', cookies=cookies)

        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_create_order(self, mock_celery_task, ac: AsyncClient):
        response = await ac.post('/order/create_order', params={
            'name': 'aaa',
            'weight': '12',
            'cost': '32',
            'order_type_name': 'Clothing',
        })

        assert response.status_code == 201
        assert type(response.json()['id']) == str

    @pytest.mark.anyio
    async def test_order_type_list(self, ac: AsyncClient):
        response = await ac.get('/order/order_type_list')

        assert response.status_code == 200
        assert response.json() == [{'id': 1, 'name': 'Clothing'}]

    @pytest.mark.anyio
    async def test_get_order_by_id(self, ac: AsyncClient):
        order_id = '34527623tcb72t'
        response = await ac.get(f'/order/{order_id}', params={'id': order_id})

        assert response.status_code == 200
        assert response.json() == {'cost': '2.00',
                                   'delivery_cost': 'Не рассчитана',
                                   'id': '34527623tcb72t',
                                   'name': 'test',
                                   'order_type_name': 'Clothing',
                                   'weight': '12.000'}
