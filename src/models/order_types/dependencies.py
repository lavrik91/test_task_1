from src.models.order_types.repository import OrderTypeRepository
from src.services.order_types import OrderTypesService


def order_type_service():
    return OrderTypesService(OrderTypeRepository)
