import httpx

from fastapi_cache.decorator import cache

from database import async_session_maker
from .models import Order


async def process_create_order(item_data, task_id):
    async with async_session_maker() as session:
        order = await create_order(item_data, session)
        delivery_cost = await get_delivery_cost(float(item_data['weight']), float(item_data['cost']))
        order.delivery_cost = delivery_cost
        await session.commit()

    return {'task': 'success'}


async def create_order(item_data, session):
    """Создание записи в бд заказа"""
    order = Order(**item_data)
    session.add(order)
    await session.commit()
    return order


@cache(expire=300)
async def get_price_usd():
    """Курс USD на данный момент"""
    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
    data = response.json()
    usd_to_rub_rate = data['Valute']['USD']['Value']
    return usd_to_rub_rate


async def get_delivery_cost(weight: float, cost: float) -> str:
    """Расчет цены за доставку заказа"""
    usd_to_rub_rate = await get_price_usd()
    delivery_cost = round((weight * 0.5 + cost * 0.01) * usd_to_rub_rate, 2)
    return str(delivery_cost)
