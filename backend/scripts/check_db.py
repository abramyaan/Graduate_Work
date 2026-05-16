"""
Скрипт для проверки подключения к БД
Запуск: python -m backend.scripts.check_db
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import text

from backend.db.database import SessionLocal, engine
from backend.core.config import settings


def check_connection():
    """Проверка подключения к БД"""
    print("\n" + "=" * 60)
    print("Проверка подключения к PostgreSQL")
    print("=" * 60)

    # Выводим параметры подключения (без пароля)
    db_url = settings.DATABASE_URL
    # Скрываем пароль в URL
    if "@" in db_url:
        parts = db_url.split("@")
        host_part = parts[1] if len(parts) > 1 else "???"
        user_part = parts[0].split("://")[1].split(":")[0] if "://" in parts[0] else "???"
        print(f"\n📊 Параметры подключения:")
        print(f"   Хост: {host_part}")
        print(f"   Пользователь: {user_part}")
    else:
        print(f"\n📊 URL БД: {db_url}")

    print("\n🔌 Попытка подключения...")

    try:
        # Проверяем подключение через движок
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Подключение успешно!")
            print(f"\n🐘 PostgreSQL версия:")
            print(f"   {version}")

        # Создаём сессию и проверяем базовые операции
        print("\n🔍 Проверка сессии...")
        db = SessionLocal()
        try:
            # Проверяем текущую БД
            result = db.execute(text("SELECT current_database()"))
            current_db = result.scalar()
            print(f"   База данных: {current_db}")

            # Проверяем количество таблиц
            result = db.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"   Таблиц в БД: {table_count}")

            if table_count == 0:
                print("\n⚠️  Таблицы не созданы!")
                print("   Запустите: python -m backend.scripts.init_data")
            elif table_count < 18:
                print(f"\n⚠️  Неполная структура БД (ожидается 18 таблиц)")
                print("   Запустите: python -m backend.scripts.init_data")
            else:
                print("   ✅ Структура БД полная (18 таблиц)")

                # Проверяем справочники
                print("\n📋 Проверка справочных данных:")

                # Роли
                result = db.execute(text("SELECT COUNT(*) FROM user_role"))
                roles_count = result.scalar()
                print(f"   Ролей: {roles_count} {'✅' if roles_count >= 3 else '⚠️ (ожидается >= 3)'}")

                # Категории оценки
                result = db.execute(text("SELECT COUNT(*) FROM evaluation_category"))
                categories_count = result.scalar()
                print(f"   Категорий оценки: {categories_count} {'✅' if categories_count >= 4 else '⚠️ (ожидается >= 4)'}")

                # Правила рекомендаций
                result = db.execute(text("SELECT COUNT(*) FROM recommendation_rule"))
                rules_count = result.scalar()
                print(f"   Правил рекомендаций: {rules_count} {'✅' if rules_count >= 3 else '⚠️ (ожидается >= 3)'}")

                # Пользователи
                result = db.execute(text("SELECT COUNT(*) FROM user_account"))
                users_count = result.scalar()
                print(f"   Пользователей: {users_count}")

                if users_count == 0:
                    print("\n💡 Создайте администратора:")
                    print("   python -m backend.scripts.create_admin")

        finally:
            db.close()

        print("\n" + "=" * 60)
        print("✅ Проверка завершена успешно")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Ошибка подключения к БД!")
        print(f"\n📝 Детали ошибки:")
        print(f"   {type(e).__name__}: {e}")

        print(f"\n🔧 Возможные решения:")
        print(f"   1. Проверьте, что PostgreSQL запущен")
        print(f"   2. Проверьте параметры в .env файле")
        print(f"   3. Убедитесь, что база данных существует:")
        print(f"      CREATE DATABASE resume_db;")
        print(f"   4. Проверьте права пользователя БД")

        print("\n" + "=" * 60 + "\n")
        return False


if __name__ == "__main__":
    success = check_connection()
    sys.exit(0 if success else 1)
