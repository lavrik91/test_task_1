import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import Response, Request

from src.database.models import UserSession
from src.models.user_session.task.tasks_cookie import (
    get_or_create_user_session,
    create_user_session_and_set_cookie,
<<<<<<< HEAD
    set_session_cookie,
=======
>>>>>>> 7b4a077 (10 commit (ref test))
)


@pytest.fixture
def mock_request_response():
    # Создаем моки для Request и Response
    request = AsyncMock(spec=Request)
    response = AsyncMock(spec=Response)
    # Устанавливаем пустые куки по умолчанию
    request.cookies = {}
    response.cookies = {}
    return request, response


class MockSession:
    def __init__(self, repo):
        self.repo = repo

    async def create(self, peyload):
        return UserSession(id=21, session_id="mocked_session_id")


class TestUserSession:

    async def test_get_or_create_user_session_new_session(self, mock_request_response):
        request, response = mock_request_response

        # Мокаем асинхронную функцию create_user_session_and_set_cookie
        new_session_id = str(uuid.uuid4())
        mock_create_user_session_and_set_cookie = AsyncMock(return_value=new_session_id)

        # Заменяем реальную функцию временно на заглушку в контексте теста
        with patch(
                'src.models.user_session.task.tasks_cookie.create_user_session_and_set_cookie',
                mock_create_user_session_and_set_cookie
        ):
            session_id = await get_or_create_user_session(response, request)

            # Проверяем, что функция была вызвана и куки установлены
            mock_create_user_session_and_set_cookie.assert_called_once_with(response)
            assert session_id == new_session_id

    async def test_get_or_create_user_session_old_session(self, mock_request_response):
        request, response = mock_request_response
        old_id = 'old_cookie_value'
        request.cookies['session_id'] = old_id

        # Мокаем асинхронную функцию create_user_session_and_set_cookie
        new_session_id = str(uuid.uuid4())
        mock_create_user_session_and_set_cookie = AsyncMock(return_value=new_session_id)

        # Заменяем реальную функцию временно на заглушку в контексте теста
        with patch(
                'src.models.user_session.task.tasks_cookie.create_user_session_and_set_cookie',
                mock_create_user_session_and_set_cookie
        ):
            session_id = await get_or_create_user_session(response, request)

            # Проверяем, что функция create_user_session_and_set_cookie не была вызвана
            mock_create_user_session_and_set_cookie.assert_not_called()

        assert session_id == old_id

    async def test_create_user_session_and_set_cookie(self, mock_request_response):
        _, response = mock_request_response

        mock_set_session_cookie = MagicMock()
        with patch('src.models.user_session.task.tasks_cookie.UserSessionService', MockSession), \
                patch('src.models.user_session.task.tasks_cookie.set_session_cookie', mock_set_session_cookie):
            # Вызываем тестируемую функцию
            session_id = await create_user_session_and_set_cookie(response)

            assert session_id == "mocked_session_id"

            # Проверяем, что функция set_session_cookie была вызвана с правильными аргументами
            mock_set_session_cookie.assert_called_once_with(response,
                                                            "mocked_session_id")  # Подставьте ожидаемый session_id

    def test_set_session_cookie(self):
        # Создаем мок объекта Response
        mock_response = MagicMock(spec=Response)

        # Вызываем функцию, которую тестируем
        session_id = "test_session_id"
        set_session_cookie(mock_response, session_id)

        # Проверяем, что метод set_cookie был вызван с правильными аргументами
        mock_response.set_cookie.assert_called_once_with(key='session_id', value=session_id)

        # Можно также проверить, что вызов произошел только один раз
        assert mock_response.set_cookie.call_count == 1
