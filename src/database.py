from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import settings

DATABASE_URL = settings.DB_URL

engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with Session() as session:
#         yield session
