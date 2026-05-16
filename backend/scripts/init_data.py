"""
Скрипт для инициализации справочных данных в БД
Создаёт:
- Роли пользователей
- Категории оценки с весами
- Правила рекомендаций

Запуск: python -m backend.scripts.init_data
"""
import sys
from pathlib import Path
from decimal import Decimal

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.exc import IntegrityError

from backend.db.database import SessionLocal, engine
from backend.models.models import (
    Base,
    UserRole,
    EvaluationCategory,
    RecommendationRule
)


def init_user_roles():
    """Инициализация ролей пользователей"""
    print("\n📋 Инициализация ролей пользователей...")
    db = SessionLocal()

    roles = [
        {"role_name": "Администратор", "role_shortname": "Admin"},
        {"role_name": "Рекрутер", "role_shortname": "Recruiter"},
        {"role_name": "Оператор", "role_shortname": "Operator"},
    ]

    try:
        for role_data in roles:
            existing = db.query(UserRole).filter(
                UserRole.role_name == role_data["role_name"]
            ).first()

            if not existing:
                new_role = UserRole(**role_data)
                db.add(new_role)
                db.flush()
                print(f"   ✅ Создана роль: {role_data['role_name']} (ID: {new_role.role_id})")
            else:
                print(f"   ℹ️  Роль уже существует: {role_data['role_name']} (ID: {existing.role_id})")

        db.commit()
        print("✅ Роли пользователей инициализированы")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при инициализации ролей: {e}")
        raise
    finally:
        db.close()


def init_evaluation_categories():
    """Инициализация категорий оценки с весами"""
    print("\n⚖️  Инициализация категорий оценки...")
    db = SessionLocal()

    # Веса категорий согласно CLAUDE.md:
    # навыки 40%, опыт 30%, структура 20%, ATS 10%
    categories = [
        {"name": "Навыки", "weight": Decimal("0.40")},
        {"name": "Опыт", "weight": Decimal("0.30")},
        {"name": "Структура резюме", "weight": Decimal("0.20")},
        {"name": "ATS-совместимость", "weight": Decimal("0.10")},
    ]

    try:
        for cat_data in categories:
            existing = db.query(EvaluationCategory).filter(
                EvaluationCategory.name == cat_data["name"]
            ).first()

            if not existing:
                new_category = EvaluationCategory(**cat_data)
                db.add(new_category)
                db.flush()
                print(f"   ✅ Создана категория: {cat_data['name']} "
                      f"(вес: {float(cat_data['weight'])*100:.0f}%, ID: {new_category.category_id})")
            else:
                # Обновляем вес, если он изменился
                if existing.weight != cat_data["weight"]:
                    existing.weight = cat_data["weight"]
                    print(f"   🔄 Обновлён вес категории: {cat_data['name']} "
                          f"(новый вес: {float(cat_data['weight'])*100:.0f}%)")
                else:
                    print(f"   ℹ️  Категория уже существует: {cat_data['name']} "
                          f"(вес: {float(existing.weight)*100:.0f}%, ID: {existing.category_id})")

        db.commit()

        # Проверка: сумма весов должна быть 1.0
        total_weight = db.query(
            EvaluationCategory
        ).with_entities(
            EvaluationCategory.weight
        ).all()
        total = sum(float(w[0]) for w in total_weight)

        if abs(total - 1.0) < 0.01:
            print(f"✅ Категории оценки инициализированы (сумма весов: {total:.2f})")
        else:
            print(f"⚠️  Предупреждение: сумма весов = {total:.2f}, ожидалось 1.00")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при инициализации категорий: {e}")
        raise
    finally:
        db.close()


def init_recommendation_rules():
    """Инициализация правил рекомендаций"""
    print("\n🎯 Инициализация правил рекомендаций...")
    db = SessionLocal()

    # Правила согласно CLAUDE.md:
    # >= 75 → «Пригласить немедленно»
    # 50-74 → «Отложить»
    # < 50 → «Отклонить»
    rules = [
        {
            "min_score": Decimal("75.00"),
            "max_score": Decimal("100.00"),
            "recommendation_text": "Пригласить немедленно"
        },
        {
            "min_score": Decimal("50.00"),
            "max_score": Decimal("74.99"),
            "recommendation_text": "Отложить"
        },
        {
            "min_score": Decimal("0.00"),
            "max_score": Decimal("49.99"),
            "recommendation_text": "Отклонить"
        },
    ]

    try:
        for rule_data in rules:
            existing = db.query(RecommendationRule).filter(
                RecommendationRule.recommendation_text == rule_data["recommendation_text"]
            ).first()

            if not existing:
                new_rule = RecommendationRule(**rule_data)
                db.add(new_rule)
                db.flush()
                print(f"   ✅ Создано правило: {rule_data['recommendation_text']} "
                      f"(балл: {float(rule_data['min_score']):.0f}-{float(rule_data['max_score']):.0f}, "
                      f"ID: {new_rule.recommendation_id})")
            else:
                # Обновляем пороги, если они изменились
                updated = False
                if existing.min_score != rule_data["min_score"]:
                    existing.min_score = rule_data["min_score"]
                    updated = True
                if existing.max_score != rule_data["max_score"]:
                    existing.max_score = rule_data["max_score"]
                    updated = True

                if updated:
                    print(f"   🔄 Обновлены пороги: {rule_data['recommendation_text']} "
                          f"({float(rule_data['min_score']):.0f}-{float(rule_data['max_score']):.0f})")
                else:
                    print(f"   ℹ️  Правило уже существует: {rule_data['recommendation_text']} "
                          f"({float(existing.min_score):.0f}-{float(existing.max_score):.0f}, "
                          f"ID: {existing.recommendation_id})")

        db.commit()
        print("✅ Правила рекомендаций инициализированы")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при инициализации правил: {e}")
        raise
    finally:
        db.close()


def main():
    """Главная функция инициализации"""
    print("\n" + "=" * 60)
    print("Инициализация справочных данных системы")
    print("=" * 60)

    # Создаём структуру БД
    print("\n🔧 Создание структуры БД...")
    Base.metadata.create_all(bind=engine)
    print("✅ Структура БД готова")

    # Инициализируем справочники
    init_user_roles()
    init_evaluation_categories()
    init_recommendation_rules()

    print("\n" + "=" * 60)
    print("✅ Инициализация завершена успешно!")
    print("=" * 60)
    print("\n💡 Следующий шаг: создайте администратора")
    print("   python -m backend.scripts.create_admin")
    print("\n")


if __name__ == "__main__":
    main()
