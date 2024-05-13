from repository.order_type import OrderTypeRepository, OrderRepository
from services.order import OrderService


def order_service():
    return OrderService(OrderRepository)


def order_type_service():
    return OrderService(OrderTypeRepository)
