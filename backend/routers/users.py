import core.schemas as schemas
from core.auth import (create_access_token, get_current_user,
                       get_password_hash, verify_password)
from core.database import get_session
from core.model_utils import create_model, delete_model, get_user_by_username
from core.models import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login", response_model=schemas.LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """Произвести авторизацию пользователя"""
    user = await get_user_by_username(form_data.username, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=schemas.UserResponse)
async def create_user(
    user_data: schemas.UserPost,
    db: AsyncSession = Depends(get_session),
):
    """Создать нового пользователя"""
    if await get_user_by_username(user_data.username, db):
        raise HTTPException(status_code=404, detail="User already exist")
    user_data.full_name = (
        user_data.full_name if user_data.full_name else user_data.username
    )
    user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    await create_model(db, user)
    return schemas.UserResponse(
        username=user.username, full_name=user.full_name, created_at=user.created_at
    )


@router.get("/me", response_model=schemas.UserResponse)
async def get_info_user(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)
):
    """Получить полную информацию о себе"""
    return schemas.UserResponse(
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        created_at=user.created_at,
    )


@router.get("/all", response_model=schemas.UserList)
async def get_users(db: AsyncSession = Depends(get_session)):
    """Получить список всех пользователей"""
    users = (await db.scalars(select(User))).all()
    return schemas.UserList(
        users=[
            schemas.User(username=user.username, full_name=user.full_name)
            for user in users
        ]
    )


@router.get("/{username}", response_model=schemas.User)
async def get_user(username: str, db: AsyncSession = Depends(get_session)):
    """Получить информацию о конкретном пользователе"""
    user = await get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return schemas.User(username=user.username, full_name=user.full_name)


@router.patch("/", response_model=schemas.UserPatchResponse)
async def update_info_user(
    user_data: schemas.UserPatch,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Изменить данные пользователя"""
    if user_data.username:
        if await get_user_by_username(user_data.username, db):
            raise HTTPException(
                status_code=404, detail="A user with this username already exists"
            )
        user.username = user_data.username
    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    await db.commit()
    if user_data.username or user_data.full_name or user_data.password:
        return schemas.UserPatchResponse(
            message=schemas.User(username=user.username, full_name=user.full_name)
        )
    else:
        return schemas.UserPatchResponse(message="No changes")


@router.delete("/")
async def delete_user(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)
):
    """Удалить пользователя"""
    await delete_model(db, user)
    return {"message": "User deleted"}
