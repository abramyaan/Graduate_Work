"""
Роутер для работы со специализациями
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db.database import get_db
from backend.models.models import Specialization

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_specializations(
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех специализаций"""
    query = select(Specialization)
    result = await db.execute(query)
    specializations = result.scalars().all()

    return [
        {
            "specialization_id": spec.specialization_id,
            "name": spec.name
        }
        for spec in specializations
    ]
