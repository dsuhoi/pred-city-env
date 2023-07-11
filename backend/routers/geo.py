import core.model_utils as model_utils
import core.models as models
import core.schemas as schemas
from core.database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/location/{zip}", description="Получение локации по zip коду.")
async def get_location(zip: int, db: AsyncSession = Depends(get_session)):
    if loc := await model_utils.get_location(db, zip):
        return schemas.Location.from_orm(loc)
    else:
        raise HTTPException(
            status_code=404, detail="There is no location for such zip."
        )


@router.get("/", description="Получение всех данных о местоположении объектов.")
async def get_geo(db: AsyncSession = Depends(get_session)):
    cargo = [
        schemas.CargoLocation.from_orm(cg)
        for cg in await model_utils.get_all(db, models.Cargo)
    ]
    cars = [
        schemas.CarLocation.from_orm(car)
        for car in await model_utils.get_all(db, models.Car)
    ]
    return schemas.GeoResponse(cargo=cargo, cars=cars)
