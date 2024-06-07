from src.order.models import OrderType, Order
from src.utils.repository import SQLAlchemyRepository
from src.database import Session


class OrderTypeRepository(SQLAlchemyRepository[OrderType]):
    model = OrderType


class OrderRepository(SQLAlchemyRepository[Order]):
    model = Order
