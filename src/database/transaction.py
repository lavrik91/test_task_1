from functools import wraps

from loguru import logger
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.database.database import CTX_SESSION, get_session


def transaction(coro):
    """
    Decorator for handling SQLAlchemy database transactions asynchronously.

    Usage:
        @transaction
        async def some_async_function(...):
                ...

    :param coro: Coroutine function to decorate.
    :return: Decorated coroutine function with transaction handling.
    """
    @wraps(coro)
    async def inner(*args, **kwargs):
        session: AsyncSession = get_session()
        CTX_SESSION.set(session)

        try:
            result = await coro(*args, **kwargs)
            await session.commit()
            return result
        except HTTPException as error:
            logger.opt(exception=True).error(f"Rolling back changes.\n{error.detail}", exc_info=True)
            await session.rollback()
            raise error
        except (IntegrityError, PendingRollbackError) as error:
            logger.error(f"Rolling back changes.\n{error.detail}", exc_info=True)
            await session.rollback()
        finally:
            await session.close()

    return inner

