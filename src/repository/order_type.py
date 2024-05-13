from utils.repository import SQLAlchemyRepository
from order.models import OrderType, Order


class OrderTypeRepository(SQLAlchemyRepository):
    model = OrderType


class OrderRepository(SQLAlchemyRepository):
    model = Order
