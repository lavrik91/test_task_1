from src.order.models import OrderType, Order
from src.utils.repository import SQLAlchemyRepository
from src.database import Session


class OrderTypeRepository(SQLAlchemyRepository):
    model = OrderType
    session = Session

class OrderRepository(SQLAlchemyRepository):
    model = Order
    session = Session
