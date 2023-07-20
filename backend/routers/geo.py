from typing import Annotated

import core.model_utils as model_utils
import core.models as models
import core.schemas as schemas
from core.database import get_session
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get(
    "/cities",
    description="Получение списка всех городов.",
)
async def get_cities(
    limit: Annotated[int, Query(gt=0, description="Ограничение запросов")] = None,
    geojson: Annotated[bool, Query(description="Флаг форматирования в GeoJSON")] = None,
    db: AsyncSession = Depends(get_session),
):
    if geojson:
        return await model_utils.get_cities_geojson(db)
    return [
        schemas.CityList.parse_obj(c)
        for c in await model_utils.get_all(db, models.City, limit=limit)
    ]


@router.get(
    "/cities/{id}",
    response_model=schemas.City,
    description="Получение полной информации по городу.",
)
async def get_city(
    id: int,
    with_districts: Annotated[
        bool, Query(description="Флаг добавления информации о районах")
    ] = None,
    with_blocks: Annotated[
        bool, Query(description="Флаг добавления информации о кварталах")
    ] = None,
    with_geometry: Annotated[
        bool, Query(description="Флаг добавления геоданных")
    ] = None,
    db: AsyncSession = Depends(get_session),
):
    if data := await model_utils.get_by_id(db, models.City, id):
        res = schemas.City.parse_obj(data)

        if not with_geometry:
            del res.geometry
        if not with_districts:
            del res.districts
        if not with_blocks:
            del res.blocks
        return res
    else:
        raise HTTPException(status_code=404, detail="There is no city for such id.")


@router.get(
    "/districts",
    description="Получение списка всех районов.",
)
async def get_districts(
    city_id: Annotated[int, Query(gt=0, description="ID города")] = None,
    limit: Annotated[int, Query(gt=0, description="Ограничение запросов")] = None,
    geojson: Annotated[bool, Query(description="Флаг форматирования в GeoJSON")] = None,
    db: AsyncSession = Depends(get_session),
):
    if geojson:
        return await model_utils.get_districts_geojson(db)
    cond = lambda x: True
    if city_id:
        cond = lambda x: x.city_id == city_id
    return [
        schemas.DistrictList.parse_obj(d)
        for d in await model_utils.get_all(db, models.District, limit=limit)
        if cond(d)
    ]


@router.get(
    "/districts/{id}",
    response_model=schemas.District,
    description="Получение полной информации по району.",
)
async def get_district(
    id: int,
    with_geometry: Annotated[
        bool, Query(description="Флаг добавления геоданных")
    ] = None,
    db: AsyncSession = Depends(get_session),
):
    if data := await model_utils.get_by_id(db, models.District, id):
        res = schemas.District.parse_obj(data)

        if not with_geometry:
            del res.geometry
        return res
    else:
        raise HTTPException(status_code=404, detail="There is no district for such id.")


@router.get(
    "/blocks",
    description="Получение списка всех кварталов.",
)
async def get_districts(
    limit: Annotated[int, Query(gt=0, description="Ограничение запросов")] = None,
    geojson: Annotated[bool, Query(description="Флаг форматирования в GeoJSON")] = None,
    db: AsyncSession = Depends(get_session),
):
    if geojson:
        return await model_utils.get_blocks_geojson(db)
    return [
        schemas.BlockList.parse_obj(d)
        for d in await model_utils.get_all(db, models.Block, limit=limit)
    ]


@router.get(
    "/blocks/{id}",
    response_model=schemas.Block,
    description="Получение полной информации по кварталу.",
)
async def get_district(
    id: int,
    with_geometry: Annotated[
        bool, Query(description="Флаг добавления геоданных")
    ] = None,
    db: AsyncSession = Depends(get_session),
):
    if data := await model_utils.get_by_id(db, models.Block, id):
        res = schemas.Block.parse_obj(data)

        if not with_geometry:
            del res.geometry
        return res
    else:
        raise HTTPException(status_code=404, detail="There is no block for such id.")
