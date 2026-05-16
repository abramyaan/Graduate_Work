"""
Роутер для работы с кандидатами
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.db.database import get_db
from backend.models.models import Candidate, Resume
from backend.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateWithResumes,
)

router = APIRouter()


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать нового кандидата"""
    # Проверка на дубликат email если он указан
    if candidate_data.email:
        result = await db.execute(
            select(Candidate).where(Candidate.email == candidate_data.email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Кандидат с email {candidate_data.email} уже существует"
            )

    # Создание кандидата
    candidate = Candidate(**candidate_data.model_dump())
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)

    return candidate


@router.get("/", response_model=List[CandidateWithResumes])
async def get_candidates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех кандидатов"""
    # Запрос с подсчётом резюме для каждого кандидата
    query = (
        select(Candidate, func.count(Resume.resume_id).label("resume_count"))
        .outerjoin(Resume)
        .group_by(Candidate.candidate_id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    results = result.all()

    # Формирование ответа
    candidates = []
    for candidate, resume_count in results:
        candidate_dict = CandidateWithResumes.model_validate(candidate).model_dump()
        candidate_dict["resume_count"] = resume_count
        candidates.append(CandidateWithResumes(**candidate_dict))

    return candidates


@router.get("/{candidate_id}", response_model=CandidateWithResumes)
async def get_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить кандидата по ID"""
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Подсчёт резюме
    result = await db.execute(
        select(func.count(Resume.resume_id)).where(Resume.candidate_id == candidate_id)
    )
    resume_count = result.scalar()

    candidate_dict = CandidateWithResumes.model_validate(candidate).model_dump()
    candidate_dict["resume_count"] = resume_count

    return CandidateWithResumes(**candidate_dict)


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить кандидата"""
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Проверка на дубликат email если он обновляется
    if candidate_data.email and candidate_data.email != candidate.email:
        result = await db.execute(
            select(Candidate).where(Candidate.email == candidate_data.email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Кандидат с email {candidate_data.email} уже существует"
            )

    # Обновление полей
    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.commit()
    await db.refresh(candidate)

    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить кандидата"""
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Проверка на наличие резюме
    result = await db.execute(
        select(func.count(Resume.resume_id)).where(Resume.candidate_id == candidate_id)
    )
    resume_count = result.scalar()

    if resume_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить кандидата: у него есть {resume_count} резюме"
        )

    db.delete(candidate)
    await db.commit()

    return None
