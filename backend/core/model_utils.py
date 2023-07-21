from types import FunctionType

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base
from .models import (Block, Block_property, City, City_property, District,
                     District_property, User)


async def get_user_by_id(id: int, db: AsyncSession) -> User:
    query = sa.select(User).where(User.id == id)
    return (await db.scalars(query)).first()


async def get_user_by_username(username: str, db: AsyncSession) -> User:
    query = sa.select(User).where(User.username == username)
    return (await db.scalars(query)).first()


async def get_count(db: AsyncSession, model: Base):
    return (await db.scalars(sa.sql.func.count(model.id))).first()


async def get_where(db: AsyncSession, model: Base, condition: FunctionType):
    return (await db.scalars(sa.select(model).where(condition(model)))).first()


async def get_by_id(db: AsyncSession, model: Base, id: int):
    return await get_where(db, model, lambda x: x.id == id)


async def get_all(db: AsyncSession, model: Base, limit: int = None):
    if limit:
        return (await db.scalars(sa.select(model).limit(limit))).all()
    return (await db.scalars(sa.select(model))).all()


async def get_all_where(
    db: AsyncSession, model: Base, condition: FunctionType = None, limit: int = None
):
    if limit:
        return (
            await db.scalars(sa.select(model).where(condition(model)).limit(limit))
        ).all()
    return (await db.scalars(sa.select(model).where(condition(model)))).all()


def exec_query_geojson(func_query):
    """Getting data from the database in the form of GeoJSON"""

    async def wrapper(db: AsyncSession, *args, **kwargs):
        query = func_query(*args, **kwargs)
        data = (await db.execute(query)).first()[0]
        if data["features"]:
            return data
        return {}

    wrapper.__name__ = func_query.__name__
    return wrapper


@exec_query_geojson
def get_blocks_geojson(city_id: int):
    return (
        sa.select(
            sa.func.json_build_object(
                "type",
                "FeatureCollection",
                "features",
                sa.func.json_agg(
                    sa.func.json_build_object(
                        "type",
                        "Feature",
                        "properties",
                        sa.func.json_build_object(
                            "title",
                            Block.title,
                            "population",
                            Block_property.population,
                            "area",
                            Block_property.area,
                        ),
                        "geometry",
                        sa.func.ST_AsGeoJSON(Block.geom).cast(sa.JSON),
                    )
                ),
            )
        )
        .select_from(Block)
        .outerjoin(Block_property, Block.id == Block_property.block_id)
        .where(Block.city_id == city_id)
    )


@exec_query_geojson
def get_districts_geojson(city_id: int):
    return (
        sa.select(
            sa.func.json_build_object(
                "type",
                "FeatureCollection",
                "features",
                sa.func.json_agg(
                    sa.func.json_build_object(
                        "type",
                        "Feature",
                        "properties",
                        sa.func.json_build_object(
                            "title",
                            District.title,
                            "population",
                            District_property.population,
                            "area",
                            District_property.area,
                        ),
                        "geometry",
                        sa.func.ST_AsGeoJSON(District.geom).cast(sa.JSON),
                    )
                ),
            )
        )
        .select_from(District)
        .outerjoin(District_property, District.id == District_property.district_id)
        .where(District.city_id == city_id)
    )


@exec_query_geojson
def get_cities_geojson():
    return (
        sa.select(
            sa.func.json_build_object(
                "type",
                "FeatureCollection",
                "features",
                sa.func.json_agg(
                    sa.func.json_build_object(
                        "type",
                        "Feature",
                        "properties",
                        sa.func.json_build_object(
                            "title",
                            City.title,
                            "population",
                            City_property.population,
                            "area",
                            City_property.area,
                        ),
                        "geometry",
                        sa.func.ST_AsGeoJSON(City.geom).cast(sa.JSON),
                    )
                ),
            )
        )
        .select_from(City)
        .outerjoin(City_property, City.id == City_property.city_id)
    )


async def create_model(db: AsyncSession, model: Base):
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


async def delete_model(db: AsyncSession, model: Base):
    await db.delete(model)
    await db.commit()
