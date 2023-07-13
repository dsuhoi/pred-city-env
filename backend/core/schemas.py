from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

Lat = Annotated[float, Field(example=10.345, description="Широта")]
Lng = Annotated[float, Field(example=10.345, description="Долгота")]

Password = Annotated[str, Field(example="password", description="Пароль пользователя")]
Username = Annotated[
    str,
    Field(pattern=r"^[0-9a-z]+$", example="user123", description="Логин пользователя"),
]

Fullname = Annotated[str, Field(description="ФИО пользователя")]

Datetime = Annotated[datetime, Field(description="Дата регистрации")]


class User(BaseModel):
    username: Username
    full_name: Fullname | None = None


class UserResponse(User):
    role: str
    created_at: Datetime

    class Config:
        from_attributes = True


class UserPost(User):
    password: Password


class UserList(BaseModel):
    users: list[User]


class UserPatch(BaseModel):
    username: Username | None = None
    full_name: Fullname | None = None
    password: Password | None = None


class UserPatchResponse(BaseModel):
    message: User | str


class LoginResponse(BaseModel):
    access_token: str = Field(description="Токен аутентификации")
    token_type: str = Field(description="Тип токена")
