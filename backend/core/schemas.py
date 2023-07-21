from datetime import datetime
from typing import Annotated

import shapely
from pydantic import BaseModel, Field, HttpUrl

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


class Properties(BaseModel):
    # title: str
    common_area: float = Field(gt=0, description="Общая площадь(км^2)")
    beers_per_square_km: float = Field(
        ge=0, description="Количестов пивных магазинов на км^2"
    )
    shop_numbers: int = Field(ge=0, description="Количество магазинов")
    green_area: float = Field(ge=0, description="Площадь озелененной территории")
    station_numbers: int = Field(ge=0, description="Количество остановок")
    avg_altitude_apartments: float | None = Field(description="Высотность зданий")
    garage_area: float = Field(ge=0, description="Площадь гаражных территорий")
    retail_area: float = Field(ge=0, description="Площадь рынков и овощебаз")

    class Config:
        from_attributes = True


class PropertiesCity(BaseModel):
    class Config:
        from_attributes = True


class Geometry(BaseModel):
    type: str
    coordinates: list


class CityInfo(BaseModel):
    title: str = Field(description="Название города")

    class Config:
        from_attributes = True


class DistrictList(BaseModel):
    id: int
    title: str = Field(description="Название района")

    class Config:
        from_attributes = True


class District(BaseModel):
    title: str = Field(description="Название района")
    properties: Properties
    city: CityInfo
    geometry: Geometry

    class Config:
        from_attributes = True


class BlockList(BaseModel):
    id: int
    title: str = Field(description="Название квартала")

    class Config:
        from_attributes = True


class Block(BaseModel):
    title: str = Field(description="Название района")
    properties: Properties
    city: CityInfo
    geometry: Geometry

    class Config:
        from_attributes = True


class CityList(BaseModel):
    id: int
    title: str = Field(description="Название города")

    class Config:
        from_attributes = True


class City(BaseModel):
    title: str = Field(description="Название города")
    properties: PropertiesCity
    districts: list[DistrictList] | None
    blocks: list[BlockList] | None
    geometry: Geometry

    class Config:
        from_attributes = True


class LinksList(BaseModel):
    links: list[HttpUrl]
