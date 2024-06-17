from src.models.order.repository import OrderRepository
from src.services.order import OrderService


def order_service():
    return OrderService(OrderRepository)


