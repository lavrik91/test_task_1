from src.repository.order_type import OrderTypeRepository, OrderRepository
from src.services.order import OrderService


def order_service():
    return OrderService(OrderRepository)


def order_type_service():
    return OrderService(OrderTypeRepository)
