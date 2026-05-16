"""
Простой скрипт для создания администратора (без эмодзи для Windows)
Запуск: python -m backend.scripts.create_admin_simple
"""
import sys
from datetime import date
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from backend.db.database import SessionLocal, sync_engine
from backend.models.models import Base, UserRole, UserAccount


# Контекст для хэширования паролей (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хэширование пароля с использованием bcrypt"""
    return pwd_context.hash(password)


def create_admin():
    """Создаёт администратора в БД"""
    print("=" * 60)
    print("Создание администратора")
    print("=" * 60)

    # Создаём таблицы, если их ещё нет
    print("\n1. Проверка структуры БД...")
    Base.metadata.create_all(bind=sync_engine)
    print("OK - Структура БД готова")

    # Создаём сессию
    db = SessionLocal()

    try:
        # Шаг 1: Получаем роль "Администратор"
        print("\n2. Поиск роли 'Администратор'...")
        admin_role = db.query(UserRole).filter(UserRole.role_name == "Администратор").first()

        if not admin_role:
            print("ОШИБКА: Роль 'Администратор' не найдена!")
            print("Запустите сначала: docker exec -i resume_postgres psql -U user -d resume_db < db/schema.sql")
            return False

        print(f"OK - Роль найдена (ID: {admin_role.role_id})")

        # Шаг 2: Проверяем, существует ли пользователь
        login = "admin"
        print(f"\n3. Проверка пользователя '{login}'...")
        existing_user = db.query(UserAccount).filter(UserAccount.login == login).first()

        if existing_user:
            print(f"ВНИМАНИЕ: Пользователь '{login}' уже существует!")
            print(f"   ID: {existing_user.user_id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Роль: {existing_user.role.role_name}")
            return True

        # Шаг 3: Хэшируем пароль
        password = "admin123"
        print("\n4. Хэширование пароля...")
        password_hash = hash_password(password)
        print(f"OK - Пароль захэширован (длина: {len(password_hash)} символов)")

        # Шаг 4: Создаём пользователя
        print(f"\n5. Создание пользователя '{login}'...")
        new_user = UserAccount(
            login=login,
            password_hash=password_hash,
            email="admin@system.local",
            last_name="Администратор",
            first_name="Системный",
            patronymic=None,
            registration_date=date.today(),
            role_id=admin_role.role_id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print("\n" + "=" * 60)
        print("УСПЕХ: Администратор создан!")
        print("=" * 60)
        print(f"\nДанные для входа:")
        print(f"   Логин:    {new_user.login}")
        print(f"   Пароль:   {password}")
        print(f"   Email:    {new_user.email}")
        print(f"   ФИО:      {new_user.last_name} {new_user.first_name}")
        print(f"   Роль:     {new_user.role.role_name}")
        print(f"   User ID:  {new_user.user_id}")
        print(f"   Дата рег: {new_user.registration_date}")
        print("\nТеперь можно войти в систему через фронтенд!")
        print("=" * 60 + "\n")
        return True

    except IntegrityError as e:
        db.rollback()
        print(f"\nОШИБКА: Пользователь с таким логином или email уже существует")
        print(f"   Детали: {e}")
        return False
    except Exception as e:
        db.rollback()
        print(f"\nОШИБКА: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\nИнициализация системы\n")
    success = create_admin()
    sys.exit(0 if success else 1)
