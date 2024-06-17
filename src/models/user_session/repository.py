from src.database.models import UserSession
from src.database.repository import SQLAlchemyRepository


class UserSessionRepository(SQLAlchemyRepository[UserSession]):
    model = UserSession
