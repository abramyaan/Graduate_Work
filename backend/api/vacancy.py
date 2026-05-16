"""
Роутер для работы с вакансиями
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

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
def create_vacancy(
    vacancy_data: VacancyCreate,
    db: Session = Depends(get_db)
):
    """Создать новую вакансию"""
    # Проверка существования специализации
    specialization = db.get(Specialization, vacancy_data.specialization_id)
    if not specialization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Специализация с ID {vacancy_data.specialization_id} не найдена"
        )

    # Создание вакансии
    vacancy = Vacancy(**vacancy_data.model_dump())
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)

    return vacancy


@router.get("/", response_model=List[VacancyWithSpecialization])
def get_vacancies(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Получить список всех вакансий"""
    query = select(Vacancy).join(Specialization)

    if is_active is not None:
        query = query.where(Vacancy.is_active == is_active)

    query = query.offset(skip).limit(limit)
    vacancies = db.execute(query).scalars().all()

    # Добавление названия специализации
    result = []
    for vacancy in vacancies:
        vacancy_dict = VacancyWithSpecialization.model_validate(vacancy).model_dump()
        vacancy_dict["specialization_name"] = vacancy.specialization.name
        result.append(VacancyWithSpecialization(**vacancy_dict))

    return result


@router.get("/{vacancy_id}", response_model=VacancyWithSpecialization)
def get_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db)
):
    """Получить вакансию по ID"""
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вакансия с ID {vacancy_id} не найдена"
        )

    vacancy_dict = VacancyWithSpecialization.model_validate(vacancy).model_dump()
    vacancy_dict["specialization_name"] = vacancy.specialization.name

    return VacancyWithSpecialization(**vacancy_dict)


@router.put("/{vacancy_id}", response_model=VacancyResponse)
def update_vacancy(
    vacancy_id: int,
    vacancy_data: VacancyUpdate,
    db: Session = Depends(get_db)
):
    """Обновить вакансию"""
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вакансия с ID {vacancy_id} не найдена"
        )

    # Проверка специализации если она обновляется
    if vacancy_data.specialization_id is not None:
        specialization = db.get(Specialization, vacancy_data.specialization_id)
        if not specialization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Специализация с ID {vacancy_data.specialization_id} не найдена"
            )

    # Обновление полей
    update_data = vacancy_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vacancy, field, value)

    db.commit()
    db.refresh(vacancy)

    return vacancy


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vacancy(
    vacancy_id: int,
    db: Session = Depends(get_db)
):
    """Удалить вакансию (soft delete - устанавливает is_active = False)"""
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вакансия с ID {vacancy_id} не найдена"
        )

    # Soft delete
    vacancy.is_active = False
    db.commit()

    return None
