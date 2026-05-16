"""
Роутер для работы с кандидатами
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db)
):
    """Создать нового кандидата"""
    # Проверка на дубликат email если он указан
    if candidate_data.email:
        existing = db.execute(
            select(Candidate).where(Candidate.email == candidate_data.email)
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Кандидат с email {candidate_data.email} уже существует"
            )

    # Создание кандидата
    candidate = Candidate(**candidate_data.model_dump())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


@router.get("/", response_model=List[CandidateWithResumes])
def get_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
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

    results = db.execute(query).all()

    # Формирование ответа
    candidates = []
    for candidate, resume_count in results:
        candidate_dict = CandidateWithResumes.model_validate(candidate).model_dump()
        candidate_dict["resume_count"] = resume_count
        candidates.append(CandidateWithResumes(**candidate_dict))

    return candidates


@router.get("/{candidate_id}", response_model=CandidateWithResumes)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Получить кандидата по ID"""
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Подсчёт резюме
    resume_count = db.execute(
        select(func.count(Resume.resume_id)).where(Resume.candidate_id == candidate_id)
    ).scalar()

    candidate_dict = CandidateWithResumes.model_validate(candidate).model_dump()
    candidate_dict["resume_count"] = resume_count

    return CandidateWithResumes(**candidate_dict)


@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: Session = Depends(get_db)
):
    """Обновить кандидата"""
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Проверка на дубликат email если он обновляется
    if candidate_data.email and candidate_data.email != candidate.email:
        existing = db.execute(
            select(Candidate).where(Candidate.email == candidate_data.email)
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Кандидат с email {candidate_data.email} уже существует"
            )

    # Обновление полей
    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)

    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Удалить кандидата"""
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Проверка на наличие резюме
    resume_count = db.execute(
        select(func.count(Resume.resume_id)).where(Resume.candidate_id == candidate_id)
    ).scalar()

    if resume_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить кандидата: у него есть {resume_count} резюме"
        )

    db.delete(candidate)
    db.commit()

    return None
