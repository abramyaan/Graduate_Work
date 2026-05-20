"""
Модуль оценки соответствия резюме вакансии

Использует дообученную модель sentence-transformers для:
1. Генерации эмбеддингов резюме и вакансии
2. Вычисления косинусного сходства
3. Расчёта взвешенного балла по категориям
4. Определения рекомендации
"""

import os
import re
from typing import Dict, List, Optional, Set
from decimal import Decimal

import torch
from sentence_transformers import SentenceTransformer


# =============================================================================
# Конфигурация
# =============================================================================

DEFAULT_MODEL_PATH = "ml/models/finetuned_model"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Веса категорий оценки (из CLAUDE.md)
CATEGORY_WEIGHTS = {
    "Навыки": 0.40,
    "Опыт": 0.30,
    "Структура": 0.20,
    "ATS-совместимость": 0.10,
}

# Технические термины для ATS (не склоняются, используются в оригинальном виде)
TECH_TERMS = {
    # Языки программирования
    'python', 'java', 'javascript', 'typescript', 'go', 'golang', 'php', 'ruby',
    'c++', 'c#', 'swift', 'kotlin', 'rust', 'scala', 'perl', 'r', 'matlab',

    # Фреймворки и библиотеки
    'django', 'flask', 'fastapi', 'react', 'vue', 'angular', 'node', 'nodejs',
    'express', 'spring', 'laravel', 'rails', 'asp.net', 'net', '.net',

    # Базы данных
    'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'cassandra',
    'elasticsearch', 'clickhouse', 'oracle', 'mssql', 'sqlite', 'dynamodb',

    # DevOps и инфраструктура
    'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github', 'git',
    'aws', 'azure', 'gcp', 'terraform', 'ansible', 'prometheus', 'grafana',
    'nginx', 'apache', 'linux', 'ubuntu', 'centos', 'debian',

    # Очереди и стримы
    'kafka', 'rabbitmq', 'celery', 'airflow',

    # Тестирование
    'pytest', 'unittest', 'jest', 'selenium', 'cypress',

    # Другие технологии
    'rest', 'api', 'graphql', 'grpc', 'microservices', 'ci/cd', 'agile', 'scrum',
    'sql', 'nosql', 'orm', 'sqlalchemy', 'pandas', 'numpy', 'tensorflow', 'pytorch',
}


# =============================================================================
# Вспомогательные функции для анализа текста
# =============================================================================

def calculate_ats_score(resume_text: str, vacancy_text: str) -> float:
    """
    Рассчитать ATS-совместимость на основе технических терминов

    ATS (Applicant Tracking System) проверяет наличие ключевых
    технических терминов из вакансии в резюме.

    Логика:
    1. Найти какие технические термины упоминаются в вакансии
    2. Проверить какие из них есть в резюме
    3. Процент совпадения = (термины в резюме / термины в вакансии) * 100

    Args:
        resume_text: текст резюме
        vacancy_text: текст вакансии

    Returns:
        ats_score: процент совпадения технических терминов (0-100)
    """
    # Приведение к нижнему регистру
    resume_lower = resume_text.lower()
    vacancy_lower = vacancy_text.lower()

    # Найти какие термины требуются в вакансии
    required_terms = {term for term in TECH_TERMS if term in vacancy_lower}

    if not required_terms:
        # Если в вакансии нет технических терминов, ставим средний балл
        return 75.0

    # Найти какие из требуемых терминов есть в резюме
    matched_terms = {term for term in required_terms if term in resume_lower}

    # Процент совпадения
    ats_score = (len(matched_terms) / len(required_terms)) * 100

    return ats_score


# =============================================================================
# Загрузка модели
# =============================================================================

class ResumeEvaluator:
    """
    Класс для оценки соответствия резюме вакансии
    """

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        """
        Инициализация оценщика

        Args:
            model_path: путь к дообученной модели
        """
        print(f"🤖 Загрузка модели из {model_path}...")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Модель не найдена: {model_path}\n"
                f"Запустите сначала ml/train.py для обучения модели"
            )

        self.model = SentenceTransformer(model_path, device=DEVICE)
        self.device = DEVICE

        print(f"✅ Модель загружена на устройство: {DEVICE}")
        print(f"📐 Размерность эмбеддингов: {self.model.get_sentence_embedding_dimension()}")

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Вычислить косинусное сходство между двумя текстами

        Args:
            text1: первый текст (резюме)
            text2: второй текст (вакансия)

        Returns:
            similarity: сходство от 0.0 до 1.0
        """
        # Генерация эмбеддингов
        emb1 = self.model.encode(text1, convert_to_tensor=True, device=self.device)
        emb2 = self.model.encode(text2, convert_to_tensor=True, device=self.device)

        # Косинусное сходство: cos(A, B) = (A·B) / (||A|| × ||B||)
        # Результат от -1 до 1
        cosine_score = torch.nn.functional.cosine_similarity(
            emb1.unsqueeze(0),
            emb2.unsqueeze(0)
        ).item()

        # Нормализация в диапазон [0, 1]
        similarity = (cosine_score + 1) / 2

        return similarity

    def evaluate_categories(
        self,
        resume_text: str,
        vacancy_text: str
    ) -> Dict[str, float]:
        """
        Оценка резюме по категориям

        Категории:
        1. Навыки (40%) - косинусное сходство
        2. Опыт (30%) - косинусное сходство с небольшим штрафом
        3. Структура (20%) - косинусное сходство с умеренным штрафом
        4. ATS-совместимость (10%) - процент совпадения технических терминов

        Args:
            resume_text: текст резюме
            vacancy_text: текст вакансии

        Returns:
            scores: словарь {категория: балл 0-100}
        """
        # 1. Базовое косинусное сходство (для большинства категорий)
        cosine_similarity = self.compute_similarity(resume_text, vacancy_text)
        cosine_score = cosine_similarity * 100

        # 2. ATS-совместимость на основе технических терминов
        ats_score = calculate_ats_score(resume_text, vacancy_text)

        # 3. Формирование оценок по категориям

        # Категория "Навыки" (40%):
        # Косинусное сходство (семантическая близость навыков)
        skills_score = cosine_score

        # Категория "Опыт" (30%):
        # Косинусное сходство с небольшим штрафом
        experience_score = cosine_score * 0.95

        # Категория "Структура" (20%):
        # Косинусное сходство с умеренным штрафом
        structure_score = cosine_score * 0.90

        # Категория "ATS-совместимость" (10%):
        # Процент совпадения технических терминов из вакансии
        # (важно для прохождения автоматических систем отбора)

        scores = {
            "Навыки": skills_score,
            "Опыт": experience_score,
            "Структура": structure_score,
            "ATS-совместимость": ats_score,
        }

        return scores

    def evaluate(
        self,
        resume_text: str,
        vacancy_text: str,
        return_categories: bool = True
    ) -> Dict:
        """
        Полная оценка резюме на соответствие вакансии

        Args:
            resume_text: текст резюме
            vacancy_text: текст вакансии
            return_categories: возвращать ли оценки по категориям

        Returns:
            result: словарь с результатами оценки
            {
                "overall_score": 87.5,  # общий балл 0-100
                "category_scores": {    # баллы по категориям (опционально)
                    "Навыки": 92.0,
                    "Опыт": 87.4,
                    ...
                },
                "recommendation": "Пригласить немедленно"
            }
        """
        # Оценки по категориям
        category_scores = self.evaluate_categories(resume_text, vacancy_text)

        # Взвешенная сумма: overall = навыки×0.4 + опыт×0.3 + структура×0.2 + ATS×0.1
        overall_score = sum(
            category_scores[category] * weight
            for category, weight in CATEGORY_WEIGHTS.items()
        )

        # Определение рекомендации по порогам из CLAUDE.md
        if overall_score >= 75:
            recommendation = "Пригласить немедленно"
        elif overall_score >= 50:
            recommendation = "Отложить на рассмотрение"
        else:
            recommendation = "Отклонить"

        result = {
            "overall_score": round(overall_score, 2),
            "recommendation": recommendation,
        }

        if return_categories:
            result["category_scores"] = {
                category: round(score, 2)
                for category, score in category_scores.items()
            }

        return result

    def batch_evaluate(
        self,
        resume_texts: List[str],
        vacancy_text: str
    ) -> List[Dict]:
        """
        Пакетная оценка нескольких резюме для одной вакансии

        Args:
            resume_texts: список текстов резюме
            vacancy_text: текст вакансии

        Returns:
            results: список результатов оценки
        """
        print(f"\n📊 Пакетная оценка {len(resume_texts)} резюме...")

        results = []
        for i, resume_text in enumerate(resume_texts, 1):
            result = self.evaluate(resume_text, vacancy_text)
            result["resume_index"] = i
            results.append(result)

        # Сортировка по убыванию балла
        results.sort(key=lambda x: x["overall_score"], reverse=True)

        return results

    def analyze_matching(
        self,
        resume_text: str,
        vacancy_text: str
    ) -> Dict:
        """
        Детальный анализ соответствия резюме и вакансии

        Args:
            resume_text: текст резюме
            vacancy_text: текст вакансии

        Returns:
            analysis: словарь с детальным анализом
            {
                "matched_skills": [...],      # навыки которые есть в обоих
                "missing_skills": [...],      # навыки из вакансии которых нет в резюме
                "resume_highlights": [...],   # топ предложения из резюме
                "summary": "..."              # итоговый вывод
            }
        """
        # Приведение к нижнему регистру
        resume_lower = resume_text.lower()
        vacancy_lower = vacancy_text.lower()

        # 1. Анализ технических навыков
        # Найти какие термины требуются в вакансии
        required_skills = sorted([term for term in TECH_TERMS if term in vacancy_lower])

        # Найти какие из требуемых терминов есть в резюме
        matched_skills = sorted([term for term in required_skills if term in resume_lower])

        # Навыки которых не хватает
        missing_skills = sorted([term for term in required_skills if term not in resume_lower])

        # 2. Поиск релевантных фрагментов резюме
        # Разбиваем резюме на предложения
        sentences = re.split(r'[.!?]\s+', resume_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]  # минимум 20 символов

        if sentences:
            # Вычисляем сходство каждого предложения с вакансией
            sentence_scores = []
            for sent in sentences:
                similarity = self.compute_similarity(sent, vacancy_text)
                sentence_scores.append((sent, similarity))

            # Сортируем по убыванию сходства и берём топ-3
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            resume_highlights = [sent for sent, score in sentence_scores[:3]]
        else:
            resume_highlights = []

        # 3. Формирование итогового вывода
        total_required = len(required_skills)
        total_matched = len(matched_skills)

        if total_required > 0:
            match_percentage = (total_matched / total_required) * 100
            summary = f"Кандидат владеет {total_matched} из {total_required} требуемых навыков ({match_percentage:.0f}%)."
        else:
            summary = "В вакансии не указаны конкретные технические требования."

        # Добавляем сильные стороны
        if matched_skills:
            top_skills = matched_skills[:5]  # топ-5
            summary += f" Сильные стороны: {', '.join(top_skills)}."

        # Добавляем отсутствующие навыки
        if missing_skills:
            top_missing = missing_skills[:3]  # топ-3 отсутствующих
            summary += f" Отсутствует: {', '.join(top_missing)}."

        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "resume_highlights": resume_highlights,
            "summary": summary
        }


# =============================================================================
# Вспомогательные функции
# =============================================================================

def get_recommendation_id(overall_score: float) -> int:
    """
    Определить ID рекомендации по баллу

    Пороги из recommendation_rule в БД:
    - >= 75: recommendation_id = 1 (Пригласить немедленно)
    - 50-74: recommendation_id = 2 (Отложить)
    - < 50:  recommendation_id = 3 (Отклонить)

    Args:
        overall_score: общий балл 0-100

    Returns:
        recommendation_id: ID правила рекомендации
    """
    if overall_score >= 75:
        return 1
    elif overall_score >= 50:
        return 2
    else:
        return 3


def save_evaluation_to_db(
    resume_id: int,
    model_id: int,
    user_id: int,
    overall_score: float,
    category_scores: Dict[str, float]
) -> Optional[int]:
    """
    Сохранить результат оценки в БД

    Args:
        resume_id: ID резюме
        model_id: ID модели
        user_id: ID пользователя, запустившего оценку
        overall_score: общий балл 0-100
        category_scores: баллы по категориям

    Returns:
        result_id: ID созданной записи или None при ошибке
    """
    try:
        from backend.db.database import SessionLocal
        from backend.models.models import (
            ResultEvaluation,
            ResultCategoryScore,
            EvaluationCategory,
        )
        from decimal import Decimal

        db = SessionLocal()

        # Определение recommendation_id
        recommendation_id = get_recommendation_id(overall_score)

        # Создание записи результата
        result = ResultEvaluation(
            overall_score=Decimal(str(overall_score)),
            resume_id=resume_id,
            model_id=model_id,
            user_id=user_id,
            recommendation_id=recommendation_id,
        )
        db.add(result)
        db.flush()  # Получаем result_id

        # Получение ID категорий из БД
        categories = db.query(EvaluationCategory).all()
        category_map = {cat.name: cat.category_id for cat in categories}

        # Сохранение оценок по категориям
        for category_name, score in category_scores.items():
            if category_name in category_map:
                category_score = ResultCategoryScore(
                    result_id=result.result_id,
                    category_id=category_map[category_name],
                    score=Decimal(str(score)),
                )
                db.add(category_score)

        db.commit()

        print(f"✅ Результат оценки сохранён в БД (result_id={result.result_id})")

        result_id = result.result_id
        db.close()

        return result_id

    except ImportError:
        print("⚠️  Пропуск сохранения в БД: backend модули не найдены")
        return None
    except Exception as e:
        print(f"❌ Ошибка при сохранении в БД: {e}")
        return None


# =============================================================================
# Пример использования
# =============================================================================

def main():
    """
    Пример использования ResumeEvaluator
    """
    print("=" * 80)
    print("🎯 Оценка соответствия резюме вакансии")
    print("=" * 80)

    # Инициализация оценщика
    evaluator = ResumeEvaluator(model_path=DEFAULT_MODEL_PATH)

    # Пример резюме и вакансии
    resume = """
    Python-разработчик с опытом работы 4 года.
    Технологии: Python, Django, FastAPI, PostgreSQL, Docker, Redis.
    Разработка REST API и микросервисов.
    Опыт работы с Git, CI/CD, pytest.
    """

    vacancy = """
    Требуется Python-разработчик (Middle).
    Опыт от 3 лет.
    Обязательно: Python, FastAPI, PostgreSQL.
    Желательно: Docker, Redis, опыт написания тестов.
    """

    # Оценка
    print("\n📝 Резюме:")
    print(resume.strip())
    print("\n📋 Вакансия:")
    print(vacancy.strip())

    result = evaluator.evaluate(resume, vacancy)

    print("\n" + "=" * 80)
    print("📊 Результаты оценки:")
    print("=" * 80)
    print(f"Общий балл: {result['overall_score']:.2f}/100")
    print(f"Рекомендация: {result['recommendation']}")

    if "category_scores" in result:
        print("\nОценки по категориям:")
        for category, score in result["category_scores"].items():
            weight = CATEGORY_WEIGHTS[category]
            print(f"  {category:25} {score:6.2f}/100  (вес {weight:.0%})")

    print("=" * 80)


if __name__ == "__main__":
    main()
