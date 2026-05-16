"""
Fine-tuning модели sentence-transformers для оценки соответствия резюме вакансии

Использует CosineSimilarityLoss для обучения на парах (resume_text, vacancy_text, label)
где label от 0.0 до 1.0 обозначает степень соответствия.

Базовая модель: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
(поддерживает русский язык, 768-мерные эмбеддинги)
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader


# =============================================================================
# Конфигурация
# =============================================================================

# Пути
DATASET_PATH = "dataset/dataset_training.json"
MODEL_OUTPUT_PATH = "ml/models/finetuned_model"
BASE_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Гиперпараметры
BATCH_SIZE = 16
EPOCHS = 10
WARMUP_STEPS = 100
LEARNING_RATE = 2e-5
TRAIN_TEST_SPLIT = 0.8  # 80% на обучение, 20% на валидацию

# Устройство (GPU если доступна, иначе CPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# =============================================================================
# Загрузка датасета
# =============================================================================

def load_dataset(dataset_path: str) -> List[Dict]:
    """
    Загрузить датасет из JSON файла

    Формат датасета:
    [
        {
            "resume_text": "...",
            "vacancy_text": "...",
            "label": 0.0-1.0
        },
        ...
    ]
    """
    print(f"📂 Загрузка датасета из {dataset_path}...")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Датасет не найден: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"✅ Загружено {len(dataset)} примеров")
    return dataset


def prepare_training_data(dataset: List[Dict], split_ratio: float = 0.8):
    """
    Подготовить данные для обучения и валидации

    Возвращает:
    - train_examples: список InputExample для обучения
    - val_examples: список пар (text1, text2, score) для валидации
    """
    print(f"\n📊 Подготовка данных (train/val split: {split_ratio:.0%})...")

    # Создание InputExample для sentence-transformers
    examples = []
    for item in dataset:
        example = InputExample(
            texts=[item["resume_text"], item["vacancy_text"]],
            label=float(item["label"])
        )
        examples.append(example)

    # Разделение на train и validation
    split_idx = int(len(examples) * split_ratio)
    train_examples = examples[:split_idx]

    # Валидационный набор в формате (text1, text2, score)
    val_examples = [
        (item["resume_text"], item["vacancy_text"], float(item["label"]))
        for item in dataset[split_idx:]
    ]

    print(f"✅ Обучающая выборка: {len(train_examples)} примеров")
    print(f"✅ Валидационная выборка: {len(val_examples)} примеров")

    return train_examples, val_examples


# =============================================================================
# Fine-tuning модели
# =============================================================================

def train_model(
    train_examples: List[InputExample],
    val_examples: List[tuple],
    model_name: str = BASE_MODEL_NAME,
    output_path: str = MODEL_OUTPUT_PATH,
    batch_size: int = BATCH_SIZE,
    epochs: int = EPOCHS,
    warmup_steps: int = WARMUP_STEPS,
    learning_rate: float = LEARNING_RATE,
):
    """
    Fine-tuning модели sentence-transformers

    Args:
        train_examples: обучающие примеры (InputExample)
        val_examples: валидационные примеры для оценки
        model_name: базовая модель для fine-tuning
        output_path: путь для сохранения дообученной модели
        batch_size: размер батча
        epochs: количество эпох обучения
        warmup_steps: шаги прогрева learning rate
        learning_rate: скорость обучения
    """
    print(f"\n🤖 Загрузка базовой модели: {model_name}")
    print(f"🖥️  Устройство: {DEVICE}")

    # Загрузка базовой модели
    model = SentenceTransformer(model_name, device=DEVICE)

    print(f"📐 Размерность эмбеддингов: {model.get_sentence_embedding_dimension()}")

    # Создание DataLoader
    train_dataloader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=batch_size
    )

    # Loss функция: CosineSimilarityLoss
    # Оптимизирует косинусное сходство между эмбеддингами пары текстов
    # чтобы оно стремилось к значению label (0.0-1.0)
    train_loss = losses.CosineSimilarityLoss(model)

    print(f"\n🔥 Loss функция: CosineSimilarityLoss")
    print(f"📦 Batch size: {batch_size}")
    print(f"🔄 Epochs: {epochs}")
    print(f"🌡️  Learning rate: {learning_rate}")
    print(f"⏫ Warmup steps: {warmup_steps}")

    # Evaluator для валидации
    evaluator = None
    if val_examples:
        print(f"\n📊 Создание evaluator для валидации...")
        sentences1 = [ex[0] for ex in val_examples]
        sentences2 = [ex[1] for ex in val_examples]
        scores = [ex[2] for ex in val_examples]

        evaluator = EmbeddingSimilarityEvaluator(
            sentences1=sentences1,
            sentences2=sentences2,
            scores=scores,
            name="validation"
        )

        # Оценка до обучения
        print("\n🔍 Оценка базовой модели на валидации:")
        evaluator(model, output_path=None)

    # Создание директории для сохранения
    os.makedirs(output_path, exist_ok=True)

    # Обучение
    print(f"\n🚀 Начало fine-tuning...")
    start_time = datetime.now()

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=epochs,
        warmup_steps=warmup_steps,
        optimizer_params={'lr': learning_rate},
        output_path=output_path,
        show_progress_bar=True,
        save_best_model=True,
    )

    end_time = datetime.now()
    training_duration = (end_time - start_time).total_seconds()

    print(f"\n✅ Fine-tuning завершён!")
    print(f"⏱️  Время обучения: {training_duration:.1f} секунд ({training_duration/60:.1f} минут)")
    print(f"💾 Модель сохранена в: {output_path}")

    return model


# =============================================================================
# Тестирование дообученной модели
# =============================================================================

def test_model(model_path: str, test_examples: List[tuple]):
    """
    Тестирование дообученной модели на примерах

    Args:
        model_path: путь к дообученной модели
        test_examples: список (resume_text, vacancy_text, expected_label)
    """
    print(f"\n🧪 Тестирование модели из {model_path}...")

    model = SentenceTransformer(model_path, device=DEVICE)

    print("\n📝 Примеры предсказаний:\n")

    for i, (resume, vacancy, expected) in enumerate(test_examples[:5], 1):
        # Генерация эмбеддингов
        emb1 = model.encode(resume, convert_to_tensor=True)
        emb2 = model.encode(vacancy, convert_to_tensor=True)

        # Косинусное сходство
        cosine_score = torch.nn.functional.cosine_similarity(
            emb1.unsqueeze(0),
            emb2.unsqueeze(0)
        ).item()

        # Преобразование из [-1, 1] в [0, 1]
        similarity_score = (cosine_score + 1) / 2

        # Преобразование в процент [0, 100]
        score_percent = similarity_score * 100
        expected_percent = expected * 100

        print(f"Пример #{i}:")
        print(f"  Резюме:    {resume[:80]}...")
        print(f"  Вакансия:  {vacancy[:80]}...")
        print(f"  Ожидаемое соответствие: {expected_percent:.1f}%")
        print(f"  Предсказано:            {score_percent:.1f}%")
        print(f"  Разница:                {abs(score_percent - expected_percent):.1f}%")
        print()


# =============================================================================
# Сохранение метаданных в БД (опционально)
# =============================================================================

def save_model_to_db(model_path: str, model_name: str = "finetuned_mpnet_v1"):
    """
    Сохранить информацию о модели в БД

    Требуется подключение к PostgreSQL через SQLAlchemy
    """
    try:
        from backend.db.database import SessionLocal
        from backend.models.models import Model, ModelConfig
        from datetime import date

        db = SessionLocal()

        # Проверка существования модели с таким именем
        existing = db.query(Model).filter(Model.name == model_name).first()

        if existing:
            print(f"⚠️  Модель '{model_name}' уже существует в БД (ID={existing.model_id})")
            db.close()
            return existing.model_id

        # Создание записи модели
        model_record = Model(
            name=model_name,
            artifact_path=model_path,
            finetune_date=date.today()
        )
        db.add(model_record)
        db.flush()

        # Сохранение гиперпараметров
        configs = [
            ModelConfig(model_id=model_record.model_id, param_name="base_model_name", param_value=BASE_MODEL_NAME),
            ModelConfig(model_id=model_record.model_id, param_name="batch_size", param_value=str(BATCH_SIZE)),
            ModelConfig(model_id=model_record.model_id, param_name="epochs", param_value=str(EPOCHS)),
            ModelConfig(model_id=model_record.model_id, param_name="learning_rate", param_value=str(LEARNING_RATE)),
            ModelConfig(model_id=model_record.model_id, param_name="warmup_steps", param_value=str(WARMUP_STEPS)),
            ModelConfig(model_id=model_record.model_id, param_name="device", param_value=DEVICE),
        ]

        for config in configs:
            db.add(config)

        db.commit()

        print(f"\n💾 Модель сохранена в БД:")
        print(f"   ID: {model_record.model_id}")
        print(f"   Название: {model_record.name}")
        print(f"   Путь: {model_record.artifact_path}")
        print(f"   Дата: {model_record.finetune_date}")

        db.close()

        return model_record.model_id

    except ImportError:
        print("\n⚠️  Пропуск сохранения в БД: backend модули не найдены")
        print("   Запустите этот скрипт после установки зависимостей backend")
        return None
    except Exception as e:
        print(f"\n❌ Ошибка при сохранении модели в БД: {e}")
        return None


# =============================================================================
# Главная функция
# =============================================================================

def main():
    """
    Главная функция для запуска fine-tuning
    """
    print("=" * 80)
    print("🎓 Fine-tuning модели sentence-transformers")
    print("   для оценки соответствия резюме вакансии")
    print("=" * 80)

    # 1. Загрузка датасета
    dataset = load_dataset(DATASET_PATH)

    # 2. Подготовка данных
    train_examples, val_examples = prepare_training_data(
        dataset,
        split_ratio=TRAIN_TEST_SPLIT
    )

    # 3. Fine-tuning
    model = train_model(
        train_examples=train_examples,
        val_examples=val_examples,
        model_name=BASE_MODEL_NAME,
        output_path=MODEL_OUTPUT_PATH,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        warmup_steps=WARMUP_STEPS,
        learning_rate=LEARNING_RATE,
    )

    # 4. Тестирование
    if val_examples:
        test_model(MODEL_OUTPUT_PATH, val_examples)

    # 5. Сохранение в БД (опционально)
    print("\n" + "=" * 80)
    save_model_to_db(
        model_path=MODEL_OUTPUT_PATH,
        model_name=f"finetuned_mpnet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    print("\n" + "=" * 80)
    print("✅ Все этапы выполнены успешно!")
    print(f"📁 Модель доступна в: {MODEL_OUTPUT_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
