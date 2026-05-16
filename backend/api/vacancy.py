"""
Роутер для работы с вакансиями
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.db.database import get_db
from backend.models.models import Vacancy, Specialization
from backend.schemas.vacancy import (
    VacancyCreate,
    VacancyUpdate,
    VacancyResponse,
    VacancyWithSpecialization,
)

router = APIRouter()


@router.post("/", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую вакансию"""
    # Проверка существования специализации
    specialization = await db.get(Specialization, vacancy_data.specialization_id)
    if not specialization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Специализация с ID {vacancy_data.specialization_id} не найдена"
        )

    # Создание вакансии
    vacancy = Vacancy(**vacancy_data.model_dump())
    db.add(vacancy)
    await db.commit()
    await db.refresh(vacancy)

    return vacancy


@router.get("/", response_model=List[VacancyWithSpecialization])
async def get_vacancies(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех вакансий"""
    query = select(Vacancy).options(selectinload(Vacancy.specialization))

    if is_active is not None:
        query = query.where(Vacancy.is_active == is_active)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    vacancies = result.scalars().all()

    # Pydantic автоматически извлечет specialization_name из relationship
    return [VacancyWithSpecialization.model_validate(vacancy) for vacancy in vacancies]


@router.get("/{vacancy_id}", response_model=VacancyWithSpecialization)
async def get_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить вакансию по ID"""
    query = select(Vacancy).where(Vacancy.vacancy_id == vacancy_id).options(selectinload(Vacancy.specialization))
    result = await db.execute(query)
    vacancy = result.scalar_one_or_none()

    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вакансия с ID {vacancy_id} не найдена"
        )

    # Pydantic автоматически извлечет specialization_name из relationship
    return VacancyWithSpecialization.model_validate(vacancy)


@router.put("/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: int,
    vacancy_data: VacancyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить вакансию"""
    vacancy = await db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вакансия с ID {vacancy_id} не найдена"
        )

    # Проверка специализации если она обновляется
    if vacancy_data.specialization_id is not None:
        specialization = await db.get(Specialization, vacancy_data.specialization_id)
        if not specialization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Специализация с ID {vacancy_data.specialization_id} не найдена"
            )

    # Обновление полей
    update_data = vacancy_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vacancy, field, value)

    await db.commit()
    await db.refresh(vacancy)

    return vacancy


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить вакансию (soft delete - устанавливает is_active = False)"""
    vacancy = await db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вакансия с ID {vacancy_id} не найдена"
        )

    # Soft delete
    vacancy.is_active = False
    await db.commit()

    return None
