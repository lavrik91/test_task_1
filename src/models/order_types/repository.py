from src.database.models import OrderType
from src.database.repository import SQLAlchemyRepository


class OrderTypeRepository(SQLAlchemyRepository[OrderType]):
    model = OrderType
