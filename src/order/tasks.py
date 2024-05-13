import uuid

from fastapi import Response, Request

from .models import UserSession
from database import async_session_maker


async def get_or_create_user_session(response: Response, request: Request) -> str:
    """Проверка наличия идентификатора сессии, при отсутствии создается новый"""
    cookie_id = request.cookies.get('session_id')
    if not cookie_id:
        cookie_id = await create_user_session_and_set_cookie(response)
    return cookie_id


async def create_user_session_and_set_cookie(response: Response):
    """Создание сессии, запись в бд и установка куков для пользователя"""
    async with async_session_maker() as session:
        cookie_id = str(uuid.uuid4())
        user_session = UserSession(session_id=cookie_id)
        session.add(user_session)
        await session.commit()
        set_session_cookie(response, cookie_id)
        return cookie_id


def set_session_cookie(response: Response, session_id: str):
    """Функция для установки куков с идентификатором сессии в ответе сервера"""
    response.set_cookie(key='session_id', value=session_id)
