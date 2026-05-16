"""
Роутер для работы с резюме
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from datetime import datetime

from backend.db.database import get_db
from backend.models.models import Resume, Candidate
from backend.schemas.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeWithCandidate,
    ResumeUploadResponse,
)
from backend.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузить файл резюме (PDF или DOCX)
    """
    # Проверка формата файла
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя файла не указано"
        )

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешены только файлы PDF и DOCX"
        )

    # Проверка существования кандидата
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {candidate_id} не найден"
        )

    # Генерация уникального имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"resume_{candidate_id}_{timestamp}.{file_extension}"
    file_path = os.path.join(settings.FILES_RESUMES_PATH, safe_filename)

    # Сохранение файла
    os.makedirs(settings.FILES_RESUMES_PATH, exist_ok=True)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Создание записи в БД
    resume = Resume(
        file_path=file_path,
        file_format=file_extension,
        candidate_id=candidate_id,
        extracted_text=None  # TODO: добавить парсинг PDF/DOCX
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return ResumeUploadResponse(
        resume_id=resume.resume_id,
        file_path=resume.file_path,
        file_format=resume.file_format,
        message="Резюме успешно загружено"
    )


@router.post("/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    resume_data: ResumeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать резюме (без загрузки файла - для тестирования)"""
    # Проверка существования кандидата
    candidate = await db.get(Candidate, resume_data.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кандидат с ID {resume_data.candidate_id} не найден"
        )

    # Генерация пути к файлу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"files/resumes/resume_{resume_data.candidate_id}_{timestamp}.{resume_data.file_format}"

    resume = Resume(
        file_path=file_path,
        file_format=resume_data.file_format,
        candidate_id=resume_data.candidate_id,
        extracted_text=resume_data.extracted_text
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return resume


@router.get("/", response_model=List[ResumeWithCandidate])
async def get_resumes(
    skip: int = 0,
    limit: int = 100,
    candidate_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех резюме"""
    query = select(Resume).join(Candidate)

    if candidate_id is not None:
        query = query.where(Resume.candidate_id == candidate_id)

    query = query.offset(skip).limit(limit)
    result_query = await db.execute(query)
    resumes = result_query.scalars().all()

    # Добавление данных кандидата
    result = []
    for resume in resumes:
        resume_dict = ResumeWithCandidate.model_validate(resume).model_dump()
        resume_dict["candidate_last_name"] = resume.candidate.last_name
        resume_dict["candidate_first_name"] = resume.candidate.first_name
        resume_dict["candidate_patronymic"] = resume.candidate.patronymic
        result.append(ResumeWithCandidate(**resume_dict))

    return result


@router.get("/{resume_id}", response_model=ResumeWithCandidate)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить резюме по ID"""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резюме с ID {resume_id} не найдено"
        )

    resume_dict = ResumeWithCandidate.model_validate(resume).model_dump()
    resume_dict["candidate_last_name"] = resume.candidate.last_name
    resume_dict["candidate_first_name"] = resume.candidate.first_name
    resume_dict["candidate_patronymic"] = resume.candidate.patronymic

    return ResumeWithCandidate(**resume_dict)


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить резюме (только extracted_text)"""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резюме с ID {resume_id} не найдено"
        )

    # Обновление полей
    update_data = resume_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)

    await db.commit()
    await db.refresh(resume)

    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить резюме"""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резюме с ID {resume_id} не найдено"
        )

    # Удаление физического файла если он существует
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            # Логируем ошибку но не прерываем удаление из БД
            print(f"Ошибка при удалении файла {resume.file_path}: {e}")

    db.delete(resume)
    await db.commit()

    return None
