import core.models as models
import core.schemas as schemas
import strawberry
from core.database import get_session
from core.model_utils import get_all, get_by_id, get_location
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info


async def get_context(db: AsyncSession = Depends(get_session)):
    return {"db": db}


@strawberry.experimental.pydantic.type(model=schemas.Location)
class Location:
    zip: strawberry.auto
    city: strawberry.auto
    state_name: strawberry.auto
    lat: float
    lng: float


@strawberry.experimental.pydantic.type(model=schemas.CarFull, all_fields=True)
class Car:
    pass


@strawberry.experimental.pydantic.type(model=schemas.CargoFull)
class Cargo:
    id: strawberry.auto
    pick_up_loc: strawberry.auto
    delivery_loc: strawberry.auto
    weight: strawberry.auto
    description: str


@strawberry.type
class Query:
    @strawberry.field
    async def cars(self, info: Info) -> list[Car]:
        return [
            Car.from_pydantic(schemas.CarFull.from_orm(c))
            for c in await get_all(info.context["db"], models.Car)
        ]

    @strawberry.field
    async def get_car(self, info: Info, id: int) -> Car | None:
        return Car.from_pydantic(
            schemas.CarFull.from_orm(
                await get_by_id(info.context["db"], models.Car, id=id)
            )
        )

    @strawberry.field
    async def cargo(self, info: Info) -> list[Cargo]:
        return [
            Cargo.from_pydantic(schemas.CargoFull.from_orm(c))
            for c in await get_all(info.context["db"], models.Cargo)
        ]

    @strawberry.field
    async def location(self, info: Info, zip: schemas.Zip) -> Location | None:
        return Location.from_pydantic(
            schemas.Location.from_orm(await get_location(info.context["db"], zip))
        )


schema = strawberry.Schema(query=Query, types=[Cargo, Car, Location])
router = GraphQLRouter(schema, context_getter=get_context)
