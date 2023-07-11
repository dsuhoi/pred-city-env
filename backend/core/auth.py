from datetime import datetime, timedelta
from typing import Optional

from config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from .model_utils import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=8)
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def decode_token(token):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )
        username = payload.get("sub")
        if username is None:
            raise JWTError
    except JWTError:
        return None
    return username


async def get_current_user(
    db: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)
):
    username = decode_token(token)
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )
    user = await get_user_by_username(username, db)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )
    return user
