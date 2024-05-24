import pytest
from httpx import AsyncClient
from sqlalchemy import select

from conftest import async_session_maker, ac
from src.order.models import Order, UserSession, OrderType


# @pytest.fixture(scope='module')
# async def empty_orders():
#     async with async_session_maker() as session:
#         orders = await session.execute(select(Order))
#         for order in orders.scalars():
#             session.delete(order)
#         await session.commit()


# @pytest.mark.usefixtures('empty_orders')
class TestAPI:
    # async def test_create_order(self, ac: AsyncClient):
    #     response = await ac.post('/order/create_order', json={
    #         'name': 'test',
    #         'weight': '55',
    #         'cost': '233',
    #         'order_type_name': 'Miscellaneous',
    #     })
    #
    #     assert response.status_code == 201
    async def test_order_type_list(self, ac: AsyncClient):
        response = await ac.get('/order/order_type_list')

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_user_orders_list(self):
        ...

    async def test_get_order_by_id(self):
        ...
