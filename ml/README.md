# ML модуль — Fine-tuning и оценка резюме

Модуль для дообучения модели sentence-transformers и оценки соответствия резюме вакансии.

## Структура

```
ml/
├── __init__.py
├── train.py          # Fine-tuning модели
├── evaluate.py       # Оценка резюме
├── models/           # Сохранённые модели
│   └── finetuned_model/  (создаётся после обучения)
└── README.md
```

## Базовая модель

**paraphrase-multilingual-mpnet-base-v2**
- Поддержка русского языка
- 768-мерные эмбеддинги
- Оптимизирована для семантического поиска

## Установка зависимостей

```bash
pip install sentence-transformers torch
```

Для GPU (опционально, ускоряет обучение):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 1. Обучение модели (train.py)

### Датасет

Формат `dataset/dataset_training.json`:
```json
[
  {
    "resume_text": "Текст резюме...",
    "vacancy_text": "Текст вакансии...",
    "label": 0.92  // соответствие 0.0-1.0
  },
  ...
]
```

**Текущий датасет:** 20 примеров (80% train, 20% validation)

### Запуск обучения

```bash
python ml/train.py
```

### Гиперпараметры (можно настроить в train.py)

```python
BATCH_SIZE = 16
EPOCHS = 10
WARMUP_STEPS = 100
LEARNING_RATE = 2e-5
TRAIN_TEST_SPLIT = 0.8
```

### Процесс обучения

1. ✅ Загрузка датасета
2. ✅ Разделение на train/validation (80/20)
3. ✅ Загрузка базовой модели
4. ✅ Fine-tuning с CosineSimilarityLoss
5. ✅ Валидация на каждой эпохе
6. ✅ Сохранение лучшей модели в `ml/models/finetuned_model`
7. ✅ Тестирование на примерах
8. ✅ Сохранение метаданных в БД (опционально)

### Вывод при обучении

```
🎓 Fine-tuning модели sentence-transformers
================================================================================
📂 Загрузка датасета из dataset/dataset_training.json...
✅ Загружено 20 примеров

📊 Подготовка данных (train/val split: 80%)...
✅ Обучающая выборка: 16 примеров
✅ Валидационная выборка: 4 примеров

🤖 Загрузка базовой модели: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
🖥️  Устройство: cuda
📐 Размерность эмбеддингов: 768

🔥 Loss функция: CosineSimilarityLoss
📦 Batch size: 16
🔄 Epochs: 10
🌡️  Learning rate: 2e-05
⏫ Warmup steps: 100

🚀 Начало fine-tuning...
Epoch: 100%|███████████████████| 10/10 [05:23<00:00, 32.34s/it]

✅ Fine-tuning завершён!
⏱️  Время обучения: 323.4 секунд (5.4 минут)
💾 Модель сохранена в: ml/models/finetuned_model
```

## 2. Оценка резюме (evaluate.py)

### Класс ResumeEvaluator

```python
from ml.evaluate import ResumeEvaluator

# Инициализация
evaluator = ResumeEvaluator(model_path="ml/models/finetuned_model")

# Оценка одного резюме
result = evaluator.evaluate(
    resume_text="Python-разработчик, 4 года опыта...",
    vacancy_text="Требуется Python Middle Developer..."
)

print(result)
# {
#     "overall_score": 87.5,
#     "recommendation": "Пригласить немедленно",
#     "category_scores": {
#         "Навыки": 92.0,
#         "Опыт": 87.4,
#         "Структура": 85.5,
#         "ATS-совместимость": 80.75
#     }
# }
```

### Пакетная оценка

```python
# Оценка нескольких резюме для одной вакансии
results = evaluator.batch_evaluate(
    resume_texts=[resume1, resume2, resume3],
    vacancy_text=vacancy
)

# Результаты отсортированы по убыванию балла
for r in results:
    print(f"Резюме #{r['resume_index']}: {r['overall_score']:.1f}% - {r['recommendation']}")
```

### Запуск примера

```bash
python ml/evaluate.py
```

## 3. Веса категорий оценки

Из CLAUDE.md:
- **Навыки:** 40%
- **Опыт:** 30%
- **Структура:** 20%
- **ATS-совместимость:** 10%

Общий балл: `overall = навыки×0.4 + опыт×0.3 + структура×0.2 + ATS×0.1`

## 4. Пороги рекомендаций

Из `recommendation_rule` в БД:

| Балл | Рекомендация | recommendation_id |
|------|--------------|-------------------|
| ≥ 75 | Пригласить немедленно | 1 |
| 50-74 | Отложить на рассмотрение | 2 |
| < 50 | Отклонить | 3 |

## 5. Сохранение в БД

### Модель

```python
from ml.train import save_model_to_db

model_id = save_model_to_db(
    model_path="ml/models/finetuned_model",
    model_name="finetuned_mpnet_20260516"
)
# Сохраняется в таблицы: model, model_config
```

### Результат оценки

```python
from ml.evaluate import save_evaluation_to_db

result_id = save_evaluation_to_db(
    resume_id=23,
    model_id=1,
    user_id=11,
    overall_score=87.5,
    category_scores={
        "Навыки": 92.0,
        "Опыт": 87.4,
        "Структура": 85.5,
        "ATS-совместимость": 80.75
    }
)
# Сохраняется в таблицы: result_evaluation, result_category_score
```

## 6. Математический аппарат

### Косинусное сходство

```
cos(A, B) = (A·B) / (||A|| × ||B||)
```

Где A и B — эмбеддинги резюме и вакансии (768-мерные векторы)

Результат: от -1 (противоположные) до 1 (идентичные)

Нормализация в [0, 1]:
```python
similarity = (cosine_score + 1) / 2
```

Преобразование в проценты [0, 100]:
```python
score_percent = similarity * 100
```

### CosineSimilarityLoss

Loss функция для fine-tuning:
```
L = (1 - cos(emb1, emb2) - label)²
```

Цель: косинусное сходство должно стремиться к значению `label` из датасета.

## 7. Производительность

**CPU (Intel i7):**
- Обучение 10 эпох на 16 примерах: ~10-15 минут
- Оценка одного резюме: ~0.5-1 секунда

**GPU (CUDA):**
- Обучение 10 эпох: ~3-5 минут (ускорение в 3x)
- Оценка одного резюме: ~0.1-0.2 секунды

## 8. Улучшение модели

### Увеличение датасета

Текущий датасет — 20 примеров (для демонстрации).  
Для production рекомендуется **500-1000+ примеров**.

### Источники данных

1. Исторические данные HR (резюме + решения рекрутеров)
2. Экспертная разметка (рекрутеры оценивают пары)
3. Синтетическая генерация (аугментация существующих примеров)

### Дополнительные возможности

1. **Категориальная оценка:** разные модели для навыков, опыта, структуры
2. **Named Entity Recognition:** извлечение технологий, позиций, образования
3. **Keyword matching:** явное совпадение ключевых навыков
4. **Temporal analysis:** анализ длительности опыта, дат

## 9. Интеграция с Backend

```python
# В backend/api/result_evaluation.py
from ml.evaluate import ResumeEvaluator

evaluator = ResumeEvaluator()

@router.post("/evaluate")
def evaluate_resume_endpoint(resume_id: int, vacancy_id: int, db: Session):
    # Получение резюме и вакансии из БД
    resume = db.get(Resume, resume_id)
    vacancy = db.get(Vacancy, vacancy_id)
    
    # Оценка
    result = evaluator.evaluate(
        resume.extracted_text,
        vacancy.description
    )
    
    # Сохранение в БД
    # ...
    
    return result
```

## Troubleshooting

### ImportError: No module named 'sentence_transformers'

```bash
pip install sentence-transformers
```

### CUDA out of memory

Уменьшите `BATCH_SIZE` в `train.py`:
```python
BATCH_SIZE = 8  # вместо 16
```

### Модель не найдена

Убедитесь, что запустили `python ml/train.py` перед использованием `evaluate.py`

---

**Документация:** [CLAUDE.md](../CLAUDE.md) | [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md)
