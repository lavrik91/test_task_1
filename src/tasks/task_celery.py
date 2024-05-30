import httpx
from fastapi_cache.decorator import cache

from src.order.dependencies import order_service
from src.utils.extra_logger import cel_logger


async def process_create_order(item_data: dict) -> dict:
    service = order_service()

    order = await service.create_order(item_data)
    delivery_cost = await get_delivery_cost(float(item_data['weight']), float(item_data['cost']))
    await service.update_order({'delivery_cost': delivery_cost}, order)
    return {'task': 'success'}


@cache(expire=300)
async def get_price_usd() -> float:
    """Курс USD на данный момент"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
        data = response.json()
        usd_to_rub_rate = data['Valute']['USD']['Value']
        return usd_to_rub_rate
    except Exception as e:
        cel_logger.error(f"Error when receiving the USD exchange rate: {e}")


async def get_delivery_cost(weight: float, cost: float) -> str:
    """Расчет цены за доставку заказа"""
    try:
        usd_to_rub_rate = await get_price_usd()
        delivery_cost = str(round((weight * 0.5 + cost * 0.01) * usd_to_rub_rate, 2))
        return delivery_cost
    except Exception as e:
        cel_logger.error(f"Error in calculating the shipping cost: {e}")
