from httpx import AsyncClient


async def test_add_specific_operations(ac: AsyncClient):
    response = await ac.post('/operations', json={
        "id": 1,
        "quantity": "25.5",
        "figi": "figi_CODE",
        "instrument_type": "bond",
        "date": "2024-02-15T08:51:03.438",
        "type": "Выплата купонов"
    })
    assert response.status_code == 200