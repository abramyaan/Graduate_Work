# Контекст: ПИС интеллектуальной оценки резюме

## Цель системы
Автоматизация первичного скрининга кандидатов — система загружает резюме
и вакансию, запускает семантический анализ через дообученную модель
sentence-transformers и возвращает ранжированный список кандидатов с баллами
по категориям и рекомендацией (пригласить / отложить / отклонить).

## Участники и роли
| Роль | Что делает |
|------|-----------|
| Оператор | Загружает резюме (PDF/DOCX) и вакансии, запускает оценку, загружает датасет для дообучения |
| Рекрутер | Просматривает ранжированный список кандидатов и отчёты, принимает решения |
| Администратор | Управляет пользователями, настраивает категории оценки и пороги рекомендаций |

## Информационные потоки
| № | Название | Направление | Таблицы БД |
|---|----------|-------------|------------|
| ИП1 | Запрос на проведение оценки | Оператор → ПИС | result_evaluation |
| ИП2 | Описание вакансии | Оператор → ПИС | vacancy, vacancy_skill, specialization |
| ИП3 | Файлы резюме кандидатов | Оператор → ПИС | candidate, resume, resume_skill, resume_vacancy |
| ИП4 | Параметры оценки и настройки модели | Оператор → ПИС | evaluation_category, model, model_config |
| ИП5 | Датасет для дообучения модели | Оператор → ПИС | training_pair |
| ИП6 | Ранжированный список кандидатов | ПИС → Рекрутер | result_evaluation, result_category_score, recommendation_rule |
| ИП7 | Отчёт PDF/Excel | ПИС → Рекрутер | report |

## Полный список таблиц БД (18 штук)
Подробная схема каждой таблицы — в файле DATABASE_SCHEMA.md

| # | Таблица | Назначение |
|---|---------|-----------|
| 1 | user_role | Справочник ролей |
| 2 | user_account | Пользователи системы |
| 3 | candidate | Кандидаты (внешние лица) |
| 4 | specialization | Справочник специализаций |
| 5 | vacancy | Вакансии |
| 6 | skill | Справочник навыков |
| 7 | vacancy_skill | Навыки вакансии (M:M) |
| 8 | resume | Резюме кандидатов |
| 9 | resume_vacancy | Подача резюме на вакансию (M:M) |
| 10 | resume_skill | Навыки резюме (M:M) |
| 11 | evaluation_category | Категории оценки с весами |
| 12 | model | ML-модели sentence-transformers |
| 13 | model_config | Гиперпараметры моделей |
| 14 | recommendation_rule | Пороги рекомендаций |
| 15 | result_evaluation | Результаты оценки (главная таблица) |
| 16 | result_category_score | Детализация по категориям |
| 17 | training_pair | Датасет для дообучения |
| 18 | report | История отчётов |

## Порядок создания таблиц (важно для миграций)
```
1. user_role → 2. user_account → 3. candidate → 4. specialization →
5. vacancy → 6. skill → 7. vacancy_skill → 8. resume → 9. resume_vacancy →
10. resume_skill → 11. evaluation_category → 12. model → 13. model_config →
14. recommendation_rule → 15. result_evaluation → 16. result_category_score →
17. training_pair → 18. report
```

## Математический аппарат ML-модуля
1. Парсинг резюме (PDF/DOCX) → извлечение текста
2. Генерация эмбеддингов через sentence-transformers для текста резюме и вакансии
3. Косинусное сходство: score = cos(A, B) = (A·B) / (||A|| × ||B||)
4. Взвешенная сумма по категориям:
   overall = навыки×0.4 + опыт×0.3 + структура×0.2 + ATS×0.1
5. Определение рекомендации через таблицу recommendation_rule по overall_score
6. Fine-tuning: CosineSimilarityLoss на парах (resume_text, vacancy_text, label)

## Файловая система
```
files/
├── resumes/     # оригинальные PDF/DOCX резюме
├── models/      # веса дообученных моделей (.pt)
└── reports/     # сгенерированные отчёты PDF/Excel
```

## API endpoints (планируемые)
```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/vacancies
POST   /api/vacancies
GET    /api/vacancies/{id}
POST   /api/resumes/upload
GET    /api/results
POST   /api/results/evaluate
GET    /api/results/{id}
GET    /api/results/{id}/categories
POST   /api/reports/generate
GET    /api/reports/{id}/download
POST   /api/model/train
GET    /api/model/status
```

## Нормальная форма БД
Все таблицы приведены к 3НФ:
- Составные атрибуты разбиты (ФИО → last_name, first_name, patronymic)
- Транзитивные зависимости устранены (recommendation → FK вместо TEXT)
- Связующие таблицы для M:M отношений
- Справочники выделены отдельно (specialization, skill, recommendation_rule)
