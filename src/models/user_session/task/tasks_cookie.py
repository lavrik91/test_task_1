import uuid

from fastapi import Response, Request

from src.database.transaction import transaction
from src.models.user_session.repository import UserSessionRepository
from src.models.user_session.schemas import UserSessionSchemas
from src.services.user_session import UserSessionService


async def get_or_create_user_session(response: Response, request: Request) -> str:
    """
    Checks for the presence of a session identifier in cookies. If absent, creates a new session.

    Args:
        response (Response): FastAPI response object to set cookies.
        request (Request): FastAPI request object to retrieve cookies.

    Returns:
        str: Session identifier retrieved or newly created.
    """

    cookie_id = request.cookies.get('session_id')
    if not cookie_id:
        cookie_id = await create_user_session_and_set_cookie(response)
    return cookie_id


@transaction
async def create_user_session_and_set_cookie(response: Response) -> str:
    """
    Creates a new user session, stores it in the database, and sets the session ID cookie.

    Args:
        response (Response): FastAPI response object to set cookies.

    Returns:
        str: Session identifier created and set as a cookie.
    """

    service = UserSessionService(UserSessionRepository)
    cookie_id = str(uuid.uuid4())
    payload = {"session_id": cookie_id}

    cookie = await service.create(payload)
    cookie = UserSessionSchemas.model_validate(cookie)

    set_session_cookie(response, cookie.session_id)
    return cookie.session_id


def set_session_cookie(response: Response, session_id: str) -> None:
    """
    Sets the session ID cookie in the response headers.

    Args:
        response (Response): FastAPI response object to set cookies.
        session_id (str): Session identifier to set as a cookie.
    """
    response.set_cookie(key='session_id', value=session_id)
