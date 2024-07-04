import pytest
from pytest_asyncio import is_async_test
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from src.main import app
from src.database.models import *
from src.database.transaction import transaction
from src.config import settings
from data_for_tests import ORDERS_TEST, ORDER_TYPE_TEST, SESSION_TEST

# DATABASE
DATABASE_URL_TEST = settings.DB_URL
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
Base.metadata.bind = engine_test


def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    Session: async_sessionmaker = async_sessionmaker(
        engine_test, class_=AsyncSession, expire_on_commit=False
    )
    return Session()


# @pytest.fixture(autouse=True, scope='session')
# async def prepare_database():
#     print(f"{settings.DB_NAME=}")
#     assert settings.MODE == "TEST"
#     async with engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     print('DROP DATABASE')
#     async with engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    print(f"{settings.DB_NAME=}")
    assert settings.MODE == "TEST"
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


def pytest_collection_modifyitems(items):
    """
    Хук для запуска тестов в одном цикле событий.
    Добавляет декоратор ко всем асинхронным функциям.

    @pytest.mark.asyncio(scope="session")
    async def test_name_function():
        ...
    """
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope='session')
@transaction
async def empty_orders():
    # Создание записей в бд
    async with override_get_async_session() as session:
        order_type = [OrderType(**order_type) for order_type in ORDER_TYPE_TEST]
        user_session = UserSession(**SESSION_TEST)
        orders = [Order(**order) for order in ORDERS_TEST]

        session.add_all(order_type)
        session.add(user_session)
        session.add_all(orders)
        await session.commit()
