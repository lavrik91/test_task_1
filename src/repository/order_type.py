from src.order.models import OrderType, Order
from src.utils.repository import SQLAlchemyRepository


class OrderTypeRepository(SQLAlchemyRepository):
    model = OrderType


class OrderRepository(SQLAlchemyRepository):
    model = Order
