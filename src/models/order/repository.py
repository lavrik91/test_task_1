from src.database.models import Order
from src.database.repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository[Order]):
    model = Order
