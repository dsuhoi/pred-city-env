import asyncio
from typing import AsyncGenerator

import core.models as models
import pytest
import sqlalchemy as sa
from config import settings
from core.auth import get_password_hash
from core.database import Base, get_session
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from httpx import AsyncClient
from main import app
from shapely import MultiPolygon
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine_test = create_async_engine(settings.SQLALCHEMY_DATABASE_TEST_URL)
async_session_test = sa.orm.sessionmaker(
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
        # await conn.execute(sa.text("CREATE EXTENSION postgis;"))
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
        users_data = [
            ["admin", "pass", "Admin", 2],
            ["user1", "pass", "User1", 1],
            ["user2", "pass", "User2", 1],
            ["user3", "pass", "User3", 1],
        ]
        user_models = [
            models.User(
                username=u[0],
                hashed_password=get_password_hash(u[1]),
                full_name=u[2],
                role=u[3],
            )
            for u in users_data
        ]
        db.add_all(user_models)
        await db.commit()

        cities_data = [
            ["City1", [["dist1"] + [123] * 8, ["dist2"] + [234] * 8]],
            ["City2", [["dist3"] + [321] * 8, ["dist4"] + [432] * 8]],
        ]
        zero_poly = from_shape(MultiPolygon(), srid=4326)
        city_models = [
            models.City(
                title=c[0],
                properties=models.City_property(),
                districts=[
                    # models.District(
                    #     d[0],
                    #     properties=models.District_property(
                    #         common_area=d[1],
                    #         beers_per_square_km=d[2],
                    #         shop_numbers=d[3],
                    #         green_area=d[4],
                    #         station_numbers=d[5],
                    #         avg_altitude_apartments=d[6],
                    #         garage_area=d[7],
                    #         retail_area=d[8],
                    #     ),
                    #     geom=zero_poly,
                    # )
                    # for d in c[1]
                ],
                geom=zero_poly,
            )
            for c in cities_data
        ]

        db.add_all(city_models)
        await db.commit()
        print("DATA LOADED")
