"""
Скрипт для создания тестового администратора
Запуск: python -m backend.scripts.create_admin
"""
import sys
from datetime import date
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from backend.db.database import SessionLocal, engine
from backend.models.models import Base, UserRole, UserAccount


# Контекст для хэширования паролей (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хэширование пароля с использованием bcrypt"""
    return pwd_context.hash(password)


def create_admin_user(
    login: str = "admin",
    password: str = "admin123",
    email: str = "admin@example.com",
    last_name: str = "Администратор",
    first_name: str = "Системный",
    patronymic: str = None
):
    """
    Создаёт тестового администратора в БД

    Args:
        login: Логин пользователя (по умолчанию "admin")
        password: Пароль в открытом виде (по умолчанию "admin123")
        email: Email администратора
        last_name: Фамилия
        first_name: Имя
        patronymic: Отчество (опционально)
    """
    print("=" * 60)
    print("Создание тестового администратора")
    print("=" * 60)

    # Создаём таблицы, если их ещё нет
    print("\n1. Проверка структуры БД...")
    Base.metadata.create_all(bind=engine)
    print("✅ Структура БД готова")

    # Создаём сессию
    db = SessionLocal()

    try:
        # Шаг 1: Создаём или получаем роль "Администратор"
        print("\n2. Проверка роли 'Администратор'...")
        admin_role = db.query(UserRole).filter(UserRole.role_name == "Администратор").first()

        if not admin_role:
            print("   Роль 'Администратор' не найдена, создаём...")
            admin_role = UserRole(
                role_name="Администратор",
                role_shortname="Admin"
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"✅ Роль 'Администратор' создана (ID: {admin_role.role_id})")
        else:
            print(f"✅ Роль 'Администратор' уже существует (ID: {admin_role.role_id})")

        # Шаг 2: Проверяем, существует ли пользователь
        print(f"\n3. Проверка пользователя '{login}'...")
        existing_user = db.query(UserAccount).filter(UserAccount.login == login).first()

        if existing_user:
            print(f"⚠️  Пользователь '{login}' уже существует!")
            print(f"   ID: {existing_user.user_id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Роль: {existing_user.role.role_name}")
            print(f"\n💡 Если хотите пересоздать пользователя, удалите его вручную из БД")
            return

        # Шаг 3: Хэшируем пароль
        print("\n4. Хэширование пароля...")
        password_hash = hash_password(password)
        print(f"✅ Пароль захэширован (bcrypt, длина хэша: {len(password_hash)} символов)")

        # Шаг 4: Создаём пользователя
        print(f"\n5. Создание пользователя '{login}'...")
        new_user = UserAccount(
            login=login,
            password_hash=password_hash,
            email=email,
            last_name=last_name,
            first_name=first_name,
            patronymic=patronymic,
            registration_date=date.today(),
            role_id=admin_role.role_id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print("\n" + "=" * 60)
        print("✅ Администратор успешно создан!")
        print("=" * 60)
        print(f"\n📋 Данные для входа:")
        print(f"   Логин:    {new_user.login}")
        print(f"   Пароль:   {password}")
        print(f"   Email:    {new_user.email}")
        print(f"   ФИО:      {new_user.last_name} {new_user.first_name} {new_user.patronymic or ''}")
        print(f"   Роль:     {new_user.role.role_name}")
        print(f"   User ID:  {new_user.user_id}")
        print(f"   Дата рег: {new_user.registration_date}")
        print("\n🚀 Теперь можно войти в систему через фронтенд!")
        print("=" * 60 + "\n")

    except IntegrityError as e:
        db.rollback()
        print(f"\n❌ Ошибка: пользователь с таким логином или email уже существует")
        print(f"   Детали: {e}")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Непредвиденная ошибка: {e}")
        raise
    finally:
        db.close()


def create_additional_roles():
    """Создаёт дополнительные роли (Рекрутер, Оператор)"""
    print("\n📝 Создание дополнительных ролей...")
    db = SessionLocal()

    try:
        roles = [
            {"role_name": "Рекрутер", "role_shortname": "Recruiter"},
            {"role_name": "Оператор", "role_shortname": "Operator"},
        ]

        for role_data in roles:
            existing = db.query(UserRole).filter(
                UserRole.role_name == role_data["role_name"]
            ).first()

            if not existing:
                new_role = UserRole(**role_data)
                db.add(new_role)
                print(f"   ✅ Создана роль: {role_data['role_name']}")
            else:
                print(f"   ℹ️  Роль уже существует: {role_data['role_name']}")

        db.commit()
        print("✅ Все роли проверены\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании ролей: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🔧 Инициализация системы\n")

    # Создаём все необходимые роли
    create_additional_roles()

    # Создаём администратора
    create_admin_user(
        login="admin",
        password="admin123",
        email="admin@system.local",
        last_name="Администратор",
        first_name="Системный",
        patronymic=None
    )
