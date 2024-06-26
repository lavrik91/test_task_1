import httpx

from loguru import logger
from fastapi_cache.decorator import cache

from src.services.order import OrderService
from src.models.order.repository import OrderRepository


async def process_create_order(payload: dict) -> dict:
    """
    Asynchronously processes the creation of an order and calculates the delivery cost.

    Args:
        payload (dict): Dictionary containing order details.

    Returns:
        dict: Dictionary indicating the success of the task.

    Raises:
        RuntimeError: If there is an error during order creation or delivery cost calculation.

    Note:
        This function creates an order using the OrderService, calculates the delivery cost based on the item's weight
        and cost, updates the order with the calculated delivery cost, and returns a success message.
    """

    try:
        service = OrderService(OrderRepository)
        order = await service.create_order(payload)
        delivery_cost = await get_delivery_cost(float(payload['weight']), float(payload['cost']))
        await service.update_order({'delivery_cost': delivery_cost}, order.id)
        logger.info(f"Order created: task[{order.id}]")
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"Error in processing order creation: {e}")
        raise


@cache(expire=300)
async def get_price_usd() -> float:
    """
    Retrieves the current USD to RUB exchange rate from an external API.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
        data = response.json()
        usd_to_rub_rate = data['Valute']['USD']['Value']
        return usd_to_rub_rate
    except Exception as e:
        logger.error(f"Error when receiving the USD exchange rate: {e}")
        raise


async def get_delivery_cost(weight: float, cost: float) -> str:
    """
    Calculates the delivery cost for an order based on its weight and cost, using the current USD to RUB exchange rate.
    """

    try:
        usd_to_rub_rate = await get_price_usd()
        delivery_cost = str(round((weight * 0.5 + cost * 0.01) * usd_to_rub_rate, 2))
        return delivery_cost
    except Exception as e:
        logger.error(f"Error in calculating the shipping cost: {e}")
        raise
