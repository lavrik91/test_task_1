from src.repository.user_session import UserSessionRepository
from src.services.user_session import UserSessionService


def user_session_service():
    return UserSessionService(UserSessionRepository)
