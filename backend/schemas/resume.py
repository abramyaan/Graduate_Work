"""
Pydantic схемы для Resume (резюме)
"""
from datetime import date
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class ResumeBase(BaseModel):
    """Базовая схема резюме"""
    file_path: str = Field(..., min_length=1, max_length=255, description="Путь к файлу")
    file_format: Literal["pdf", "docx"] = Field(..., description="Формат файла")
    extracted_text: Optional[str] = Field(None, description="Извлечённый текст")
    candidate_id: int = Field(..., gt=0, description="ID кандидата")


class ResumeCreate(BaseModel):
    """Схема для создания резюме (без file_path - он генерируется при загрузке)"""
    file_format: Literal["pdf", "docx"]
    candidate_id: int = Field(..., gt=0)
    extracted_text: Optional[str] = None


class ResumeUpdate(BaseModel):
    """Схема для обновления резюме"""
    extracted_text: Optional[str] = None


class ResumeResponse(ResumeBase):
    """Схема ответа с данными резюме"""
    resume_id: int
    upload_date: date

    model_config = ConfigDict(from_attributes=True)


class ResumeWithCandidate(ResumeResponse):
    """Расширенная схема резюме с данными кандидата"""
    candidate_last_name: Optional[str] = None
    candidate_first_name: Optional[str] = None
    candidate_patronymic: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ResumeUploadResponse(BaseModel):
    """Схема ответа при загрузке файла резюме"""
    resume_id: int
    file_path: str
    file_format: str
    message: str = "Резюме успешно загружено"

    model_config = ConfigDict(from_attributes=True)
