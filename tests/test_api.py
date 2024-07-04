import uuid
import pytest
from unittest.mock import patch, Mock

from httpx import AsyncClient

from data_for_tests import ORDER_TYPE_TEST


@pytest.fixture
def mock_celery_task():
    fake_uuid = str(uuid.uuid4())
    with patch('src.routers.order.create_order_task.delay', return_value=Mock(id=fake_uuid)):
        yield fake_uuid


@pytest.mark.usefixtures('empty_orders')
class TestAPI:
    @pytest.mark.parametrize(
        "token, status, response_len",
        [
            ("token123", 200, 3),
            ("fake_token", 404, 1),
            (None, 401, 1)
        ]
    )
    async def test_get_user_orders_list(self, token, status, response_len, ac: AsyncClient):
        cookies = {'session_id': token}
        response = await ac.get('/order/get_user_orders_list', cookies=cookies)

        assert response.status_code == status
        response_json = response.json()
        assert len(response_json) == response_len

    async def test_create_order(self, mock_celery_task, ac: AsyncClient):
        response = await ac.post('/order/create_order', json={
            'name': 'aaa',
            'weight': '12',
            'cost': '32',
            'order_type_name': 'Clothing',
        })

        assert response.status_code == 201
        assert type(response.json()['id']) == str
        assert "session_id" in response.cookies

    @pytest.mark.parametrize(
        "name,weight, cost, order_type, status, detail",
        [
            ("test_name", -22.33, 2.11, "Clothing", 422, "Input should be greater than 0.01"),
            ("test_name", 22.33, -2.11, "Miscellaneous", 422, "Input should be greater than 0.01"),
            ("test_name", 22.333, 2.11, "Electronics", 422, "Decimal input should have no more than 2 decimal places"),
            ("test_name", 22.33, 2.111, "Electronics", 422, "Decimal input should have no more than 2 decimal places"),
            ("", 22.33, 2.11, "Electronics", 422, "String should have at least 1 character"),
            (
            "test_name", 22.33, 2.11, "fake type", 422, "Input should be 'Clothing', 'Electronics' or 'Miscellaneous'"),
        ]
    )
    async def test_create_order_validation(self, name, weight, cost, order_type, status, detail, ac: AsyncClient):
        response = await ac.post('/order/create_order', json={
            'name': name,
            'weight': weight,
            'cost': cost,
            'order_type_name': order_type,
        })

        assert response.status_code == status
        assert detail in response.text

    async def test_order_type_list(self, ac: AsyncClient):
        response = await ac.get('/type/order_type_list')

        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == 3
        assert response_json[0]['name'] == "Clothing"
        assert response_json == ORDER_TYPE_TEST

    @pytest.mark.parametrize(
        "id, expected_status, data",
        [
            ("21cbff51-a20d-4bb0-9ee1-44a60d4c07d3", 200, 'name'),
            ("21cbff51-a20d-4bb0-9ee1-44a60d4c07d4", 404, 'detail'),
            (None, 404, "detail")
        ]
    )
    async def test_get_order_by_id(self, id, expected_status, data, ac: AsyncClient):
        response = await ac.get(f'/order/{id}', params={'id': id})

        assert response.status_code == expected_status
        response_json = response.json()
        assert data in response_json
