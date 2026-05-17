"""
Роутер для работы с кандидатами
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.db.database import get_db
from backend.models.models import (
    Candidate,
    Resume,
    ResumeVacancy,
    ResumeSkill,
    ResultEvaluation,
    ResultCategoryScore,
)
from backend.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateWithResumes,
)
import os

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
    """Удалить кандидата вместе со всеми его резюме и связанными данными"""
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Получаем все резюме кандидата
    result = await db.execute(
        select(Resume).where(Resume.candidate_id == candidate_id)
    )
    resumes = result.scalars().all()

    # Для каждого резюме удаляем все зависимости
    for resume in resumes:
        resume_id = resume.resume_id

        # 1. Удаляем все result_category_score для result_evaluation этого резюме
        result_evals = await db.execute(
            select(ResultEvaluation).where(ResultEvaluation.resume_id == resume_id)
        )
        evaluations = result_evals.scalars().all()

        for evaluation in evaluations:
            # Удаляем category scores
            await db.execute(
                select(ResultCategoryScore)
                .where(ResultCategoryScore.result_id == evaluation.result_id)
            )
            category_scores = (await db.execute(
                select(ResultCategoryScore)
                .where(ResultCategoryScore.result_id == evaluation.result_id)
            )).scalars().all()

            for score in category_scores:
                await db.delete(score)

            # Удаляем оценку
            await db.delete(evaluation)

        # 2. Удаляем записи из resume_vacancy
        resume_vacancies = (await db.execute(
            select(ResumeVacancy).where(ResumeVacancy.resume_id == resume_id)
        )).scalars().all()

        for rv in resume_vacancies:
            await db.delete(rv)

        # 3. Удаляем записи из resume_skill
        resume_skills = (await db.execute(
            select(ResumeSkill).where(ResumeSkill.resume_id == resume_id)
        )).scalars().all()

        for rs in resume_skills:
            await db.delete(rs)

        # 4. Удаляем физический файл резюме
        if os.path.exists(resume.file_path):
            try:
                os.remove(resume.file_path)
            except Exception as e:
                print(f"Ошибка при удалении файла {resume.file_path}: {e}")

        # 5. Удаляем само резюме
        await db.delete(resume)

    # Наконец удаляем кандидата
    await db.delete(candidate)
    await db.commit()

    return None
