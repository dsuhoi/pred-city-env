import asyncio
from typing import AsyncGenerator

import core.models as models
import pytest
from config import settings
from core.database import Base, get_session
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine_test = create_async_engine(settings.SQLALCHEMY_DATABASE_TEST_URL)
async_session_test = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False, autocommit=False
)
Base.metadata.bind = engine_test


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_test() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def create_data():
    async with async_session_test() as db:
        loc_data = [
            [58045, "Hillsboro", "North Dakota", 47.38241, -97.02686],
            [15951, "Saint Michael", "Pennsylvania", 40.3307, -78.77209],
            [84076, "Tridell", "Utah", 40.44718, -109.84017],
            [5446, "Colchester", "Vermont", 44.5541, -73.21647],
            [12933, "Ellenburg", "New York", 44.89118, -73.84512],
            [50472, "Saint Ansgar", "Iowa", 43.42265, -92.94644],
            [34470, "Ocala", "Florida", 29.20098, -82.08262],
            [39092, "Lake", "Mississippi", 32.31489, -89.36833],
        ]

        loc_models = [
            models.Location(zip=d[0], city=d[1], state_name=d[2], lat=d[3], lng=d[4])
            for d in loc_data
        ]
        db.add_all(loc_models)
        await db.commit()
        print("DATA LOADED")
