from typing import Annotated

import core.model_utils as model_utils
import core.models as models
import core.schemas as schemas
from core.database import get_session
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/others", tags=["others"])


@router.get("/links", description="Парсинг данных на основании внешних ссылок.")
async def get_links(links: schemas.LinksList, db: AsyncSession = Depends(get_session)):
    print(links)
    return {}
