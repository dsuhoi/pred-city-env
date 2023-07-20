import asyncio
import json
import pathlib

import geoalchemy2 as gsa
# import geopandas
import shapely
import sqlalchemy as sa

from core.auth import get_password_hash
from core.model_utils import get_count

from .database import async_session, init_db
from .model_utils import get_city_and_districts
from .models import City, City_property, District, District_property, User

DATA_DIR = pathlib.Path(__file__).parent.parent.joinpath("data")


async def __spb_example_init_data():
    with open(DATA_DIR.joinpath("saint_pet.geojson"), "r") as f:
        data = json.load(f)

    districts = []
    for dist in data["features"]:
        props = dist["properties"]
        districts.append(
            District(
                title=props["district"],
                properties=District_property(
                    population=props["population"],
                    area=props["area"],
                ),
                geom=dist["geometry"],
            )
        )

    spb = City(
        title="Санкт-Петербург",
        properties=City_property(population=5600044, area=1439),
        districts=districts,
        blocks=[],
        geom=gsa.shape.from_shape(shapely.geometry.MultiPolygon(), srid=4326),
    )
    async with async_session() as db:
        db.add(spb)
        await db.commit()
    print("Successful init data!")

    # for i, dist in enumerate(data["features"]):
    #     if dist["geometry"]["type"] == "Polygon":
    #         poly = shapely.geometry.shape(dist["geometry"])
    #         mpoly = shapely.geometry.MultiPolygon([poly])
    #         gjson = geopandas.GeoSeries([mpoly]).__geo_interface__
    #         data["features"][i]["geometry"] = gjson["features"][0]["geometry"]
    # print(data)
    # with open(DATA_DIR.joinpath("saint_pet.geojson"), "w") as f:
    #     json.dump(data, f, ensure_ascii=False)


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
            await __spb_example_init_data()


async def _init_all_db():
    await init_db()
    await init_data()


if __name__ == "__main__":
    asyncio.run(_init_all_db())
