import core.models as models
import core.schemas as schemas
import strawberry
from core.auth import ...
from core.database import get_session
from core.model_utils import get_all, get_by_id, get_location
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info


async def get_context(db: AsyncSession = Depends(get_session)):
    return {"db": db}


@strawberry.experimental.pydantic.type(model=schemas.UserResponse)
class User:
    pass


@strawberry.type
class Query:
    # @strawberry.field
    # async def cars(self, info: Info) -> list[Car]:
    #     return [
    #         Car.from_pydantic(schemas.CarFull.from_orm(c))
    #         for c in await get_all(info.context["db"], models.Car)
    #     ]

@strawberry.type
class LoginSuccess:
    user: User


@strawberry.type
class LoginError:
    message: str


LoginResult = Annotated[
    Union[LoginSuccess, LoginError], strawberry.union("LoginResult")
]

@strawberry.type
class Mutation:
    @strawberry.field
    def login(self, username: str, password: str) -> LoginResult:
        # Your domain-specific authentication logic would go here
        user = 

        if user is None:
            return LoginError(message="Something went wrong")

        return LoginSuccess(user=User(username=username))


schema = strawberry.Schema(query=Query, types=[User])
router = GraphQLRouter(schema, context_getter=get_context)
