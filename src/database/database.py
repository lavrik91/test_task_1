from contextvars import ContextVar

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.orm import DeclarativeBase
from fastapi import HTTPException, status

from src.config import settings

DATABASE_URL = settings.DB_URL

engine: AsyncEngine = create_async_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


def get_session(engine: AsyncEngine | None = engine) -> AsyncSession:
    Session: async_sessionmaker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return Session()


CTX_SESSION: ContextVar[AsyncSession] = ContextVar(
    'session', default=get_session()
)


class Session:
    # All sqlalchemy errors that can be raised
    _ERRORS = (IntegrityError, PendingRollbackError)

    def __init__(self) -> None:
        self._session: AsyncSession = CTX_SESSION.get()

    async def execute(self, query):
        try:
            result = await self._session.execute(query)
            return result
        except self._ERRORS:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
