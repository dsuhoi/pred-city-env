from typing import AsyncGenerator

from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
