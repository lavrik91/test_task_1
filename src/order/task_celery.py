import httpx

from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_maker
from .models import Order
from utils.extra_logger import cel_logger

async def process_create_order(item_data: dict) -> dict:
    try:
        async with async_session_maker() as session:
            order = await create_order(item_data, session)
            delivery_cost = await get_delivery_cost(float(item_data['weight']), float(item_data['cost']))
            order.delivery_cost = delivery_cost
            await session.commit()
        return {'task': 'success'}
    except Exception as e:
        cel_logger.error(f"Произошла ошибка при создании заказа: {e}")

async def create_order(item_data: dict, session: AsyncSession):
    """Создание записи в бд заказа"""
    try:
        order = Order(**item_data)
        session.add(order)
        await session.commit()
        return order
    except Exception as e:
        cel_logger.error(f"Произошла ошибка при создании записи заказа: {e}")

async def get_price_usd() -> float:
    """Курс USD на данный момент"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
        data = response.json()
        usd_to_rub_rate = data['Valute']['USD']['Value']
        return usd_to_rub_rate
    except Exception as e:
        cel_logger.error(f"Произошла ошибка при получении курса USD: {e}")

async def get_delivery_cost(weight: float, cost: float) -> str:
    """Расчет цены за доставку заказа"""
    try:
        usd_to_rub_rate = await get_price_usd()
        delivery_cost = str(round((weight * 0.5 + cost * 0.01) * usd_to_rub_rate, 2))
        return delivery_cost
    except Exception as e:
        cel_logger.error(f"Произошла ошибка при расчете стоимости доставки: {e}")