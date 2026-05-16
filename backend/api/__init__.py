"""
Экспорт всех роутеров API
"""
from backend.api import vacancy, candidate, resume, result_evaluation

__all__ = [
    "vacancy",
    "candidate",
    "resume",
    "result_evaluation",
]
