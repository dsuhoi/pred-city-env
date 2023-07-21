import asyncio
import json
import pathlib

import geoalchemy2 as gsa
import shapely

from core.auth import get_password_hash
from core.model_utils import get_count

from .database import async_session, init_db
from .models import City, City_property, District, District_property, User

DATA_DIR = pathlib.Path(__file__).parent.parent.joinpath("data")


async def init_geo_data():
    with open(DATA_DIR.joinpath("geo_data.geojson"), "r") as f:
        data = json.load(f)

    async with async_session() as db:
        for city in data["features"]:
            districts = []
            for dist in city["districts"]["features"]:
                dist_props = dist["properties"]
                dist_title = dist_props.pop("title")
                districts.append(
                    District(
                        title=dist_title,
                        properties=District_property(**dist_props),
                        geom=dist["geometry"],
                    )
                )
            city_props = city["properties"]
            city_title = city_props.pop("title")
            city_row = City(
                title=city_title,
                properties=City_property(**city_props),
                districts=districts,
                blocks=[],
                geom=city["geometry"],
            )
            db.add(city_row)
            await db.commit()
    print("Successful init data!")


async def init_test_admin_user():
    async with async_session() as db:
        db.add(
            User(
                username="admin",
                full_name="Admin",
                hashed_password=get_password_hash("admin"),
                role=1,
            )
        )
        await db.commit()


async def init_data():
    async with async_session() as db:
        if (await get_count(db, User)) == 0:
            await init_test_admin_user()
        if (await get_count(db, City)) == 0:
            await init_geo_data()


async def _init_all_db():
    await init_db()
    await init_data()


if __name__ == "__main__":
    asyncio.run(_init_all_db())
