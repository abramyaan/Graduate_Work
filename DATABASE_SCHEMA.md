# DATABASE SCHEMA — ПИС «Интеллектуальная оценка резюме на соответствие вакансии»

## Общие сведения
- СУБД: PostgreSQL 14+
- Кодировка: UTF-8
- Схема: `public`
- Все ID: SERIAL (автоинкремент)
- Все таблицы: IF NOT EXISTS
- Язык комментариев: русский
- Нормальная форма: 3НФ

---

## НАРУШЕНИЯ 3НФ — ЧТО БЫЛО ИСПРАВЛЕНО

| Таблица | Нарушение | Исправление |
|---------|-----------|-------------|
| `candidate` | `full_name` — составной атрибут (ФИО в одном поле) | Разделено на `last_name`, `first_name`, `patronymic` |
| `user_account` | Не было ФИО сотрудника | Добавлены `last_name`, `first_name`, `patronymic` |
| `vacancy` | `title` содержал специализацию — зависимость не от PK | Добавлен справочник `specialization`, FK в `vacancy` |
| `resume` | `file_path` хранил путь и формат вместе | Выделен отдельный атрибут `file_format` |
| `resume` | `vacancy_id` — связь резюме с вакансией не атомарна | Вынесено в связующую таблицу `resume_vacancy` |
| `result_evaluation` | `vacancy_id` — транзитивная зависимость через resume → resume_vacancy | Убран, берётся через JOIN |
| `model` | `name` содержал и название и путь к файлу | Разделено на `name` и `artifact_path` |
| `report` | `file_path` хранил путь и формат вместе | Выделен `file_format` как отдельный атрибут |

---

## ИНФОРМАЦИОННЫЕ ПОТОКИ

| № | Название | Направление | Участник | Таблицы БД |
|---|----------|-------------|----------|------------|
| ИП1 | Запрос на проведение оценки резюме | Вход | Оператор → ПИС | `result_evaluation` |
| ИП2 | Описание вакансии | Вход | Оператор → ПИС | `vacancy`, `vacancy_skill`, `specialization` |
| ИП3 | Файлы резюме кандидатов | Вход | Оператор → ПИС | `candidate`, `resume`, `resume_skill`, `resume_vacancy` |
| ИП4 | Параметры оценки и настройки модели | Вход | Оператор → ПИС | `evaluation_category`, `model`, `model_config` |
| ИП5 | Датасет для дообучения модели | Вход | Оператор → ПИС | `training_pair` |
| ИП6 | Ранжированный список кандидатов с баллами | Выход | ПИС → Рекрутер | `result_evaluation`, `result_category_score`, `recommendation_rule` |
| ИП7 | Отчёт PDF/Excel | Выход | ПИС → Рекрутер | `report` |

---

## ТАБЛИЦЫ

---

### 1. `user_role` — Роли пользователей (справочник)

**3НФ:** все атрибуты атомарны, зависят только от PK. ✅

```sql
CREATE TABLE IF NOT EXISTS public.user_role (
    role_id        SERIAL PRIMARY KEY,
    role_name      VARCHAR(50) NOT NULL UNIQUE,
    role_shortname VARCHAR(20),
    CONSTRAINT check_role_name CHECK (LENGTH(role_name) > 0)
);

COMMENT ON TABLE  public.user_role IS 'Справочник ролей пользователей системы';
COMMENT ON COLUMN public.user_role.role_id        IS 'Уникальный идентификатор роли';
COMMENT ON COLUMN public.user_role.role_name      IS 'Полное название роли';
COMMENT ON COLUMN public.user_role.role_shortname IS 'Краткое обозначение роли';

INSERT INTO user_role (role_name, role_shortname) VALUES
('Администратор', 'Admin'),
('Рекрутер',      'Recruiter'),
('Оператор',      'Operator');
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| role_id | SERIAL | PK, Not Null | 1 |
| role_name | VARCHAR(50) | Not Null, Unique, LENGTH > 0 | Рекрутер |
| role_shortname | VARCHAR(20) | м.б. NULL | Recruiter |

---

### 2. `user_account` — Пользователи системы (сотрудники)

**3НФ:** ФИО разбито на три атомарных поля. Каждый атрибут зависит только от `user_id`. ✅

```sql
CREATE TABLE IF NOT EXISTS public.user_account (
    user_id           SERIAL PRIMARY KEY,
    login             VARCHAR(50)  NOT NULL UNIQUE,
    password_hash     TEXT         NOT NULL,
    email             VARCHAR(100) NOT NULL UNIQUE,
    last_name         VARCHAR(100) NOT NULL,
    first_name        VARCHAR(100) NOT NULL,
    patronymic        VARCHAR(100),
    registration_date DATE         NOT NULL DEFAULT CURRENT_DATE,
    role_id           INTEGER      NOT NULL REFERENCES user_role(role_id),
    CONSTRAINT check_login_length  CHECK (LENGTH(login) >= 5),
    CONSTRAINT check_password_hash CHECK (LENGTH(password_hash) >= 60),
    CONSTRAINT check_email_format  CHECK (
        email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT check_reg_date   CHECK (registration_date <= CURRENT_DATE),
    CONSTRAINT check_last_name  CHECK (LENGTH(last_name) > 0),
    CONSTRAINT check_first_name CHECK (LENGTH(first_name) > 0)
);

COMMENT ON TABLE  public.user_account IS 'Пользователи системы — сотрудники организации';
COMMENT ON COLUMN public.user_account.user_id           IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN public.user_account.login             IS 'Логин для входа в систему';
COMMENT ON COLUMN public.user_account.password_hash     IS 'Хеш пароля bcrypt';
COMMENT ON COLUMN public.user_account.email             IS 'Адрес электронной почты сотрудника';
COMMENT ON COLUMN public.user_account.last_name         IS 'Фамилия сотрудника';
COMMENT ON COLUMN public.user_account.first_name        IS 'Имя сотрудника';
COMMENT ON COLUMN public.user_account.patronymic        IS 'Отчество сотрудника (необязательно)';
COMMENT ON COLUMN public.user_account.registration_date IS 'Дата регистрации в системе';
COMMENT ON COLUMN public.user_account.role_id           IS 'Ссылка на роль пользователя';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| user_id | SERIAL | PK, Not Null | 1 |
| login | VARCHAR(50) | Not Null, Unique, LENGTH >= 5 | recruiter1 |
| password_hash | TEXT | Not Null, LENGTH >= 60 (bcrypt) | $2b$12$... |
| email | VARCHAR(100) | Not Null, Unique, формат email | user@company.ru |
| last_name | VARCHAR(100) | Not Null, LENGTH > 0 | Волкова |
| first_name | VARCHAR(100) | Not Null, LENGTH > 0 | Татьяна |
| patronymic | VARCHAR(100) | м.б. NULL | Викторовна |
| registration_date | DATE | Not Null, <= CURRENT_DATE | 2025-12-18 |
| role_id | INTEGER | FK → user_role, Not Null | 2 |

---

### 3. `candidate` — Кандидаты (внешние лица, не пользователи системы)

**3НФ:** `full_name` разбито на три атомарных атрибута. Каждый зависит только от `candidate_id`. ✅

```sql
CREATE TABLE IF NOT EXISTS public.candidate (
    candidate_id SERIAL PRIMARY KEY,
    last_name    VARCHAR(100) NOT NULL,
    first_name   VARCHAR(100) NOT NULL,
    patronymic   VARCHAR(100),
    email        VARCHAR(255),
    phone        VARCHAR(20),
    CONSTRAINT check_cand_last_name  CHECK (LENGTH(last_name) > 0),
    CONSTRAINT check_cand_first_name CHECK (LENGTH(first_name) > 0),
    CONSTRAINT check_cand_email CHECK (
        email IS NULL OR
        email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT check_cand_phone CHECK (
        phone IS NULL OR
        phone ~ '^\+?[0-9\s\-\(\)]{7,20}$'
    )
);

COMMENT ON TABLE  public.candidate IS 'Кандидаты — внешние лица, подающие резюме';
COMMENT ON COLUMN public.candidate.candidate_id IS 'Уникальный идентификатор кандидата';
COMMENT ON COLUMN public.candidate.last_name    IS 'Фамилия кандидата';
COMMENT ON COLUMN public.candidate.first_name   IS 'Имя кандидата';
COMMENT ON COLUMN public.candidate.patronymic   IS 'Отчество кандидата (необязательно)';
COMMENT ON COLUMN public.candidate.email        IS 'Адрес электронной почты кандидата';
COMMENT ON COLUMN public.candidate.phone        IS 'Номер телефона кандидата';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| candidate_id | SERIAL | PK, Not Null | 1 |
| last_name | VARCHAR(100) | Not Null, LENGTH > 0 | Иванов |
| first_name | VARCHAR(100) | Not Null, LENGTH > 0 | Иван |
| patronymic | VARCHAR(100) | м.б. NULL | Иванович |
| email | VARCHAR(255) | м.б. NULL, формат email | ivan@mail.ru |
| phone | VARCHAR(20) | м.б. NULL, формат телефона | +79161234567 |

---

### 4. `specialization` — Специализации (справочник, НОВАЯ)

**3НФ:** выделена из `vacancy.title` — специализация это отдельная сущность. Устраняет повторение строк «Python-разработчик» в каждой строке vacancy. ✅

```sql
CREATE TABLE IF NOT EXISTS public.specialization (
    specialization_id SERIAL PRIMARY KEY,
    name              VARCHAR(150) NOT NULL UNIQUE,
    CONSTRAINT check_spec_name CHECK (LENGTH(name) > 0)
);

COMMENT ON TABLE  public.specialization IS 'Справочник специализаций вакансий';
COMMENT ON COLUMN public.specialization.specialization_id IS 'Уникальный идентификатор специализации';
COMMENT ON COLUMN public.specialization.name              IS 'Название специализации';

INSERT INTO specialization (name) VALUES
('Python-разработчик'),
('Frontend-разработчик'),
('Data Scientist'),
('DevOps-инженер'),
('QA-инженер'),
('Аналитик данных'),
('Менеджер проектов'),
('HR-менеджер');
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| specialization_id | SERIAL | PK, Not Null | 1 |
| name | VARCHAR(150) | Not Null, Unique, LENGTH > 0 | Python-разработчик |

---

### 5. `vacancy` — Вакансии (ИП2)

**3НФ:** специализация вынесена в FK. Все оставшиеся атрибуты атомарны и зависят только от `vacancy_id`. ✅

```sql
CREATE TABLE IF NOT EXISTS public.vacancy (
    vacancy_id        SERIAL PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    description       TEXT         NOT NULL,
    specialization_id INTEGER      NOT NULL REFERENCES specialization(specialization_id),
    is_active         BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at        DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT check_vacancy_title CHECK (LENGTH(title) >= 5),
    CONSTRAINT check_vacancy_date  CHECK (created_at <= CURRENT_DATE)
);

COMMENT ON TABLE  public.vacancy IS 'Вакансии, на которые проводится оценка резюме';
COMMENT ON COLUMN public.vacancy.vacancy_id        IS 'Уникальный идентификатор вакансии';
COMMENT ON COLUMN public.vacancy.title             IS 'Заголовок вакансии';
COMMENT ON COLUMN public.vacancy.description       IS 'Полное описание требований вакансии';
COMMENT ON COLUMN public.vacancy.specialization_id IS 'Ссылка на специализацию из справочника';
COMMENT ON COLUMN public.vacancy.is_active         IS 'Признак активности вакансии';
COMMENT ON COLUMN public.vacancy.created_at        IS 'Дата создания вакансии';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| vacancy_id | SERIAL | PK, Not Null | 1 |
| title | VARCHAR(255) | Not Null, LENGTH >= 5 | Python Developer (Middle) |
| description | TEXT | Not Null | Требуется опыт от 3 лет... |
| specialization_id | INTEGER | FK → specialization, Not Null | 1 |
| is_active | BOOLEAN | Not Null, DEFAULT TRUE | true |
| created_at | DATE | Not Null, <= CURRENT_DATE | 2025-12-18 |

---

### 6. `resume` — Резюме кандидатов (ИП3)

**3НФ:** `file_format` выделен в отдельный атрибут. `vacancy_id` убран — связь с вакансией вынесена в `resume_vacancy`. ✅

```sql
CREATE TABLE IF NOT EXISTS public.resume (
    resume_id      SERIAL PRIMARY KEY,
    file_path      VARCHAR(255) NOT NULL,
    file_format    VARCHAR(10)  NOT NULL,
    extracted_text TEXT,
    upload_date    DATE         NOT NULL DEFAULT CURRENT_DATE,
    candidate_id   INTEGER      NOT NULL REFERENCES candidate(candidate_id),
    CONSTRAINT check_file_format CHECK (file_format IN ('pdf', 'docx')),
    CONSTRAINT check_upload_date CHECK (upload_date <= CURRENT_DATE),
    CONSTRAINT check_file_path   CHECK (LENGTH(file_path) > 0)
);

COMMENT ON TABLE  public.resume IS 'Загруженные резюме кандидатов';
COMMENT ON COLUMN public.resume.resume_id      IS 'Уникальный идентификатор резюме';
COMMENT ON COLUMN public.resume.file_path      IS 'Путь к файлу резюме в файловом хранилище';
COMMENT ON COLUMN public.resume.file_format    IS 'Формат файла: pdf или docx';
COMMENT ON COLUMN public.resume.extracted_text IS 'Извлечённый текст резюме после парсинга';
COMMENT ON COLUMN public.resume.upload_date    IS 'Дата загрузки файла в систему';
COMMENT ON COLUMN public.resume.candidate_id   IS 'Ссылка на кандидата';

CREATE INDEX idx_resume_candidate ON resume(candidate_id);
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| resume_id | SERIAL | PK, Not Null | 1 |
| file_path | VARCHAR(255) | Not Null, LENGTH > 0 | files/resumes/resume_23 |
| file_format | VARCHAR(10) | Not Null, IN ('pdf','docx') | pdf |
| extracted_text | TEXT | м.б. NULL | «Опыт работы 3 года Python...» |
| upload_date | DATE | Not Null, <= CURRENT_DATE | 2025-12-18 |
| candidate_id | INTEGER | FK → candidate, Not Null | 1 |

---

### 7. `resume_vacancy` — Подача резюме на вакансию (связующая, НОВАЯ)

**3НФ:** факт подачи — самостоятельный атомарный факт со своей датой. Устраняет `vacancy_id` из `resume` и транзитивную зависимость в `result_evaluation`. ✅

```sql
CREATE TABLE IF NOT EXISTS public.resume_vacancy (
    resume_id  INTEGER NOT NULL REFERENCES resume(resume_id),
    vacancy_id INTEGER NOT NULL REFERENCES vacancy(vacancy_id),
    applied_at DATE    NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (resume_id, vacancy_id),
    CONSTRAINT check_applied_date CHECK (applied_at <= CURRENT_DATE)
);

COMMENT ON TABLE  public.resume_vacancy IS 'Факт подачи резюме на конкретную вакансию';
COMMENT ON COLUMN public.resume_vacancy.resume_id  IS 'Ссылка на резюме';
COMMENT ON COLUMN public.resume_vacancy.vacancy_id IS 'Ссылка на вакансию';
COMMENT ON COLUMN public.resume_vacancy.applied_at IS 'Дата подачи резюме на вакансию';

CREATE INDEX idx_rv_vacancy ON resume_vacancy(vacancy_id);
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| resume_id | INTEGER | PK (составной), FK → resume | 23 |
| vacancy_id | INTEGER | PK (составной), FK → vacancy | 5 |
| applied_at | DATE | Not Null, <= CURRENT_DATE | 2025-12-18 |

---

### 8. `skill` — Навыки (справочник)

**3НФ:** атомарная таблица. ✅

```sql
CREATE TABLE IF NOT EXISTS public.skill (
    skill_id SERIAL PRIMARY KEY,
    name     VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT check_skill_name CHECK (LENGTH(name) > 0)
);

COMMENT ON TABLE  public.skill IS 'Справочник навыков (технологий, инструментов)';
COMMENT ON COLUMN public.skill.skill_id IS 'Уникальный идентификатор навыка';
COMMENT ON COLUMN public.skill.name     IS 'Название навыка';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| skill_id | SERIAL | PK, Not Null | 1 |
| name | VARCHAR(100) | Not Null, Unique, LENGTH > 0 | Python |

> ⚠️ В оригинальном документе ошибка: VARCHAR(5) — исправлено на VARCHAR(100).

---

### 9. `resume_skill` — Навыки резюме (связующая)

**3НФ:** составной PK, нет других атрибутов. ✅

```sql
CREATE TABLE IF NOT EXISTS public.resume_skill (
    resume_id INTEGER NOT NULL REFERENCES resume(resume_id),
    skill_id  INTEGER NOT NULL REFERENCES skill(skill_id),
    PRIMARY KEY (resume_id, skill_id)
);

COMMENT ON TABLE  public.resume_skill IS 'Навыки, указанные в резюме кандидата';
COMMENT ON COLUMN public.resume_skill.resume_id IS 'Ссылка на резюме';
COMMENT ON COLUMN public.resume_skill.skill_id  IS 'Ссылка на навык';
```

| Поле | Тип | Ограничение |
|------|-----|-------------|
| resume_id | INTEGER | PK (составной), FK → resume |
| skill_id | INTEGER | PK (составной), FK → skill |

---

### 10. `vacancy_skill` — Навыки вакансии (связующая)

**3НФ:** составной PK, нет других атрибутов. ✅

```sql
CREATE TABLE IF NOT EXISTS public.vacancy_skill (
    vacancy_id INTEGER NOT NULL REFERENCES vacancy(vacancy_id),
    skill_id   INTEGER NOT NULL REFERENCES skill(skill_id),
    PRIMARY KEY (vacancy_id, skill_id)
);

COMMENT ON TABLE  public.vacancy_skill IS 'Навыки, требуемые вакансией';
COMMENT ON COLUMN public.vacancy_skill.vacancy_id IS 'Ссылка на вакансию';
COMMENT ON COLUMN public.vacancy_skill.skill_id   IS 'Ссылка на навык';
```

| Поле | Тип | Ограничение |
|------|-----|-------------|
| vacancy_id | INTEGER | PK (составной), FK → vacancy |
| skill_id | INTEGER | PK (составной), FK → skill |

---

### 11. `evaluation_category` — Категории оценки (ИП4)

**3НФ:** все атрибуты атомарны, зависят только от PK. Сумма весов — через триггер. ✅

```sql
CREATE TABLE IF NOT EXISTS public.evaluation_category (
    category_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    weight      NUMERIC(4,2) NOT NULL,
    CONSTRAINT check_weight CHECK (weight >= 0 AND weight <= 1)
);

COMMENT ON TABLE  public.evaluation_category IS 'Категории оценки соответствия резюме вакансии';
COMMENT ON COLUMN public.evaluation_category.category_id IS 'Уникальный идентификатор категории';
COMMENT ON COLUMN public.evaluation_category.name        IS 'Название категории оценки';
COMMENT ON COLUMN public.evaluation_category.weight      IS 'Вес категории 0.00–1.00; сумма всех = 1.00';

INSERT INTO evaluation_category (name, weight) VALUES
('Навыки',            0.40),
('Опыт',              0.30),
('Структура',         0.20),
('ATS-совместимость', 0.10);

CREATE OR REPLACE FUNCTION check_weights_sum()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT ROUND(SUM(weight)::NUMERIC, 2) FROM evaluation_category) != 1.00 THEN
        RAISE EXCEPTION 'Сумма весов категорий должна равняться 1.00';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_weights
AFTER INSERT OR UPDATE ON evaluation_category
FOR EACH ROW EXECUTE FUNCTION check_weights_sum();
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| category_id | SERIAL | PK, Not Null | 1 |
| name | VARCHAR(100) | Not Null, Unique | Навыки |
| weight | NUMERIC(4,2) | Not Null, 0.00–1.00; SUM=1 через триггер | 0.40 |

---

### 12. `model` — ML-модели (ИП4)

**3НФ:** `name` и `artifact_path` разделены — это два разных атомарных атрибута. ✅

```sql
CREATE TABLE IF NOT EXISTS public.model (
    model_id      SERIAL PRIMARY KEY,
    name          VARCHAR(255) NOT NULL UNIQUE,
    artifact_path VARCHAR(255) NOT NULL,
    finetune_date DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT check_finetune_date CHECK (finetune_date <= CURRENT_DATE),
    CONSTRAINT check_artifact_path CHECK (LENGTH(artifact_path) > 0)
);

COMMENT ON TABLE  public.model IS 'ML-модели sentence-transformers для оценки соответствия';
COMMENT ON COLUMN public.model.model_id      IS 'Уникальный идентификатор модели';
COMMENT ON COLUMN public.model.name          IS 'Логическое название модели';
COMMENT ON COLUMN public.model.artifact_path IS 'Путь к файлу весов модели в хранилище';
COMMENT ON COLUMN public.model.finetune_date IS 'Дата последнего дообучения';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| model_id | SERIAL | PK, Not Null | 1 |
| name | VARCHAR(255) | Not Null, Unique | paraphrase-multilingual-mpnet-base-v2 |
| artifact_path | VARCHAR(255) | Not Null, LENGTH > 0 | files/models/model_1.pt |
| finetune_date | DATE | Not Null, <= CURRENT_DATE | 2025-12-20 |

---

### 13. `model_config` — Параметры модели (ИП4)

**3НФ:** каждый гиперпараметр — отдельная строка. ✅

```sql
CREATE TABLE IF NOT EXISTS public.model_config (
    config_id   SERIAL PRIMARY KEY,
    model_id    INTEGER      NOT NULL REFERENCES model(model_id),
    param_name  VARCHAR(100) NOT NULL,
    param_value VARCHAR(255) NOT NULL,
    CONSTRAINT uq_model_param   UNIQUE (model_id, param_name),
    CONSTRAINT check_param_name CHECK (LENGTH(param_name) > 0)
);

COMMENT ON TABLE  public.model_config IS 'Гиперпараметры дообучения ML-модели';
COMMENT ON COLUMN public.model_config.config_id   IS 'Уникальный идентификатор параметра';
COMMENT ON COLUMN public.model_config.model_id    IS 'Ссылка на модель';
COMMENT ON COLUMN public.model_config.param_name  IS 'Название гиперпараметра';
COMMENT ON COLUMN public.model_config.param_value IS 'Значение гиперпараметра';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| config_id | SERIAL | PK, Not Null | 1 |
| model_id | INTEGER | FK → model, Not Null | 1 |
| param_name | VARCHAR(100) | Not Null, UNIQUE с model_id | batch_size |
| param_value | VARCHAR(255) | Not Null | 16 |

Примеры param_name: `batch_size`, `epochs`, `learning_rate`, `warmup_steps`, `base_model_name`

---

### 14. `recommendation_rule` — Правила рекомендаций

**3НФ:** все атрибуты атомарны, транзитивных зависимостей нет. ✅

```sql
CREATE TABLE IF NOT EXISTS public.recommendation_rule (
    recommendation_id   SERIAL PRIMARY KEY,
    min_score           NUMERIC(5,2) NOT NULL,
    max_score           NUMERIC(5,2) NOT NULL,
    recommendation_text VARCHAR(100) NOT NULL,
    CONSTRAINT check_score_range CHECK (min_score >= 0 AND max_score <= 100),
    CONSTRAINT check_score_order CHECK (max_score > min_score),
    CONSTRAINT check_rec_text    CHECK (LENGTH(recommendation_text) > 0)
);

COMMENT ON TABLE  public.recommendation_rule IS 'Пороговые правила для автоматических рекомендаций';
COMMENT ON COLUMN public.recommendation_rule.recommendation_id   IS 'Уникальный идентификатор правила';
COMMENT ON COLUMN public.recommendation_rule.min_score           IS 'Минимальный балл диапазона';
COMMENT ON COLUMN public.recommendation_rule.max_score           IS 'Максимальный балл диапазона';
COMMENT ON COLUMN public.recommendation_rule.recommendation_text IS 'Текст рекомендации системы';

INSERT INTO recommendation_rule (min_score, max_score, recommendation_text) VALUES
(75.00, 100.00, 'Пригласить немедленно'),
(50.00,  74.99, 'Отложить на рассмотрение'),
( 0.00,  49.99, 'Отклонить');
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| recommendation_id | SERIAL | PK, Not Null | 1 |
| min_score | NUMERIC(5,2) | Not Null, >= 0 | 75.00 |
| max_score | NUMERIC(5,2) | Not Null, <= 100, > min_score | 100.00 |
| recommendation_text | VARCHAR(100) | Not Null, LENGTH > 0 | Пригласить немедленно |

---

### 15. `result_evaluation` — Результаты оценки (ИП6)

**3НФ:** убран `vacancy_id` — транзитивная зависимость через `resume_id → resume_vacancy → vacancy_id`. Вакансия получается через JOIN. ✅

```sql
CREATE TABLE IF NOT EXISTS public.result_evaluation (
    result_id         SERIAL PRIMARY KEY,
    overall_score     NUMERIC(5,2) NOT NULL,
    analysis_date     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resume_id         INTEGER      NOT NULL REFERENCES resume(resume_id),
    model_id          INTEGER      NOT NULL REFERENCES model(model_id),
    user_id           INTEGER      NOT NULL REFERENCES user_account(user_id),
    recommendation_id INTEGER      NOT NULL REFERENCES recommendation_rule(recommendation_id),
    CONSTRAINT check_overall_score CHECK (overall_score >= 0 AND overall_score <= 100),
    CONSTRAINT check_analysis_date CHECK (analysis_date <= CURRENT_TIMESTAMP)
);

COMMENT ON TABLE  public.result_evaluation IS 'Результаты оценки резюме на соответствие вакансии';
COMMENT ON COLUMN public.result_evaluation.result_id         IS 'Уникальный идентификатор результата';
COMMENT ON COLUMN public.result_evaluation.overall_score     IS 'Общий процент соответствия 0.00–100.00';
COMMENT ON COLUMN public.result_evaluation.analysis_date     IS 'Дата и время проведения анализа';
COMMENT ON COLUMN public.result_evaluation.resume_id         IS 'Ссылка на оцениваемое резюме';
COMMENT ON COLUMN public.result_evaluation.model_id          IS 'Ссылка на использованную модель';
COMMENT ON COLUMN public.result_evaluation.user_id           IS 'Ссылка на пользователя, запустившего анализ';
COMMENT ON COLUMN public.result_evaluation.recommendation_id IS 'Ссылка на правило рекомендации';

CREATE INDEX idx_result_resume ON result_evaluation(resume_id);
CREATE INDEX idx_result_model  ON result_evaluation(model_id);
CREATE INDEX idx_result_user   ON result_evaluation(user_id);
CREATE INDEX idx_result_date   ON result_evaluation(analysis_date);
CREATE INDEX idx_result_score  ON result_evaluation(overall_score DESC);
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| result_id | SERIAL | PK, Not Null | 1 |
| overall_score | NUMERIC(5,2) | Not Null, 0.00–100.00 | 87.50 |
| analysis_date | TIMESTAMP | Not Null, <= NOW() | 2025-12-18 14:30:00 |
| resume_id | INTEGER | FK → resume, Not Null | 23 |
| model_id | INTEGER | FK → model, Not Null | 1 |
| user_id | INTEGER | FK → user_account, Not Null | 11 |
| recommendation_id | INTEGER | FK → recommendation_rule, Not Null | 1 |

---

### 16. `result_category_score` — Детализация оценок по категориям (ИП6)

**3НФ:** единственный числовой атрибут `score` зависит от составного ключа (result_id, category_id). ✅

```sql
CREATE TABLE IF NOT EXISTS public.result_category_score (
    id          SERIAL PRIMARY KEY,
    result_id   INTEGER      NOT NULL REFERENCES result_evaluation(result_id),
    category_id INTEGER      NOT NULL REFERENCES evaluation_category(category_id),
    score       NUMERIC(5,2) NOT NULL,
    CONSTRAINT uq_result_category   UNIQUE (result_id, category_id),
    CONSTRAINT check_category_score CHECK (score >= 0 AND score <= 100)
);

COMMENT ON TABLE  public.result_category_score IS 'Детальные оценки по каждой категории для результата';
COMMENT ON COLUMN public.result_category_score.id          IS 'Уникальный идентификатор записи';
COMMENT ON COLUMN public.result_category_score.result_id   IS 'Ссылка на результат оценки';
COMMENT ON COLUMN public.result_category_score.category_id IS 'Ссылка на категорию оценки';
COMMENT ON COLUMN public.result_category_score.score       IS 'Балл по категории 0.00–100.00';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| id | SERIAL | PK, Not Null | 1 |
| result_id | INTEGER | FK → result_evaluation, Not Null | 1 |
| category_id | INTEGER | FK → evaluation_category, Not Null | 1 |
| score | NUMERIC(5,2) | Not Null, 0.00–100.00 | 92.00 |

---

### 17. `training_pair` — Датасет для дообучения (ИП5)

**3НФ:** все атрибуты атомарны, зависят только от PK. ✅

```sql
CREATE TABLE IF NOT EXISTS public.training_pair (
    pair_id      SERIAL PRIMARY KEY,
    resume_text  TEXT         NOT NULL,
    vacancy_text TEXT         NOT NULL,
    label        NUMERIC(4,3) NOT NULL,
    created_at   DATE         NOT NULL DEFAULT CURRENT_DATE,
    model_id     INTEGER      REFERENCES model(model_id),
    CONSTRAINT check_label       CHECK (label >= 0 AND label <= 1),
    CONSTRAINT check_pair_date   CHECK (created_at <= CURRENT_DATE),
    CONSTRAINT check_resume_txt  CHECK (LENGTH(resume_text) > 0),
    CONSTRAINT check_vacancy_txt CHECK (LENGTH(vacancy_text) > 0)
);

COMMENT ON TABLE  public.training_pair IS 'Датасет пар резюме-вакансия для дообучения модели';
COMMENT ON COLUMN public.training_pair.pair_id      IS 'Уникальный идентификатор пары';
COMMENT ON COLUMN public.training_pair.resume_text  IS 'Текст резюме';
COMMENT ON COLUMN public.training_pair.vacancy_text IS 'Текст вакансии';
COMMENT ON COLUMN public.training_pair.label        IS 'Метка соответствия 0.000–1.000';
COMMENT ON COLUMN public.training_pair.created_at   IS 'Дата добавления пары в датасет';
COMMENT ON COLUMN public.training_pair.model_id     IS 'Ссылка на модель, для которой добавлена пара';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| pair_id | SERIAL | PK, Not Null | 1 |
| resume_text | TEXT | Not Null, LENGTH > 0 | «Опыт Python 3 года...» |
| vacancy_text | TEXT | Not Null, LENGTH > 0 | «Требуется Python от 2 лет...» |
| label | NUMERIC(4,3) | Not Null, 0.000–1.000 | 0.910 |
| created_at | DATE | Not Null, <= CURRENT_DATE | 2025-12-18 |
| model_id | INTEGER | FK → model, м.б. NULL | 1 |

---

### 18. `report` — История отчётов (ИП7)

**3НФ:** `file_format` выделен в отдельный атрибут. Все атрибуты зависят только от PK. ✅

```sql
CREATE TABLE IF NOT EXISTS public.report (
    report_id       SERIAL PRIMARY KEY,
    file_path       VARCHAR(255) NOT NULL,
    file_format     VARCHAR(10)  NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id         INTEGER      NOT NULL REFERENCES user_account(user_id),
    vacancy_id      INTEGER      REFERENCES vacancy(vacancy_id),
    candidate_count INTEGER      NOT NULL DEFAULT 0,
    CONSTRAINT check_report_format CHECK (file_format IN ('pdf', 'xlsx')),
    CONSTRAINT check_report_date   CHECK (created_at <= CURRENT_TIMESTAMP),
    CONSTRAINT check_cand_count    CHECK (candidate_count >= 0),
    CONSTRAINT check_report_path   CHECK (LENGTH(file_path) > 0)
);

COMMENT ON TABLE  public.report IS 'История сформированных отчётов';
COMMENT ON COLUMN public.report.report_id       IS 'Уникальный идентификатор отчёта';
COMMENT ON COLUMN public.report.file_path       IS 'Путь к файлу отчёта в хранилище';
COMMENT ON COLUMN public.report.file_format     IS 'Формат файла отчёта: pdf или xlsx';
COMMENT ON COLUMN public.report.created_at      IS 'Дата и время создания отчёта';
COMMENT ON COLUMN public.report.user_id         IS 'Ссылка на пользователя, создавшего отчёт';
COMMENT ON COLUMN public.report.vacancy_id      IS 'Ссылка на вакансию (если отчёт по конкретной)';
COMMENT ON COLUMN public.report.candidate_count IS 'Количество кандидатов в отчёте';
```

| Поле | Тип | Ограничение | Пример |
|------|-----|-------------|--------|
| report_id | SERIAL | PK, Not Null | 1 |
| file_path | VARCHAR(255) | Not Null, LENGTH > 0 | files/reports/report_1 |
| file_format | VARCHAR(10) | Not Null, IN ('pdf','xlsx') | pdf |
| created_at | TIMESTAMP | Not Null, <= NOW() | 2025-12-18 14:35:00 |
| user_id | INTEGER | FK → user_account, Not Null | 11 |
| vacancy_id | INTEGER | FK → vacancy, м.б. NULL | 5 |
| candidate_count | INTEGER | Not Null, >= 0 | 23 |

---

## ПРЕДСТАВЛЕНИЯ (VIEW)

```sql
CREATE OR REPLACE VIEW v_evaluation_history AS
SELECT
    re.result_id,
    ua.last_name || ' ' || ua.first_name                          AS user_name,
    re.analysis_date,
    re.overall_score,
    rr.recommendation_text,
    v.title                                                        AS vacancy_title,
    r.file_path,
    r.file_format,
    c.last_name || ' ' || c.first_name ||
        COALESCE(' ' || c.patronymic, '')                         AS candidate_name
FROM result_evaluation  re
JOIN user_account        ua ON re.user_id          = ua.user_id
JOIN resume               r ON re.resume_id        = r.resume_id
JOIN candidate            c ON r.candidate_id      = c.candidate_id
JOIN recommendation_rule rr ON re.recommendation_id = rr.recommendation_id
LEFT JOIN resume_vacancy  rv ON r.resume_id        = rv.resume_id
LEFT JOIN vacancy          v ON rv.vacancy_id      = v.vacancy_id
ORDER BY re.analysis_date DESC;

CREATE OR REPLACE VIEW v_ranked_candidates AS
SELECT
    re.result_id,
    c.last_name,
    c.first_name,
    c.patronymic,
    c.email,
    re.overall_score,
    rr.recommendation_text,
    v.title  AS vacancy_title,
    re.analysis_date
FROM result_evaluation  re
JOIN resume               r  ON re.resume_id         = r.resume_id
JOIN candidate            c  ON r.candidate_id       = c.candidate_id
JOIN recommendation_rule rr  ON re.recommendation_id = rr.recommendation_id
LEFT JOIN resume_vacancy  rv ON r.resume_id          = rv.resume_id
LEFT JOIN vacancy          v ON rv.vacancy_id        = v.vacancy_id
ORDER BY re.overall_score DESC;
```

---

## МАТРИЦА ДОСТУПА

| Таблица | АБД | Прогр. | Рекрутер | Оператор |
|---------|-----|--------|----------|----------|
| user_role | RIUD | RIU | R | R |
| user_account | RIUD | RIU | R | RIU |
| candidate | RIUD | RIU | R | RIU |
| specialization | RIUD | RIU | R | RIU |
| vacancy | RIUD | RIU | R | RIU |
| resume | RIUD | RIU | R | RIU |
| resume_vacancy | RIUD | RIU | R | RIU |
| skill | RIUD | RIU | R | RIU |
| resume_skill | RIUD | RIU | R | RIU |
| vacancy_skill | RIUD | RIU | R | RIU |
| evaluation_category | RIUD | RIU | — | RIU |
| model | RIUD | RIU | — | RIU |
| model_config | RIUD | RIU | — | RIU |
| recommendation_rule | RIUD | RIU | R | R |
| result_evaluation | RIUD | RIU | R | R |
| result_category_score | RIUD | RIU | R | R |
| training_pair | RIUD | RIU | — | RIU |
| report | RIUD | RIU | R | R |

R=Read, I=Insert, U=Update, D=Delete

---

## ПОРЯДОК СОЗДАНИЯ ТАБЛИЦ (по зависимостям FK)

```
1.  user_role
2.  user_account          (→ user_role)
3.  candidate
4.  specialization
5.  vacancy               (→ specialization)
6.  skill
7.  vacancy_skill         (→ vacancy, skill)
8.  resume                (→ candidate)
9.  resume_vacancy        (→ resume, vacancy)
10. resume_skill          (→ resume, skill)
11. evaluation_category
12. model
13. model_config          (→ model)
14. recommendation_rule
15. result_evaluation     (→ resume, model, user_account, recommendation_rule)
16. result_category_score (→ result_evaluation, evaluation_category)
17. training_pair         (→ model)
18. report                (→ user_account, vacancy)
```

---

## ИТОГОВЫЙ СОСТАВ

| Тип | Кол-во |
|-----|--------|
| Таблицы | 18 |
| Представления (VIEW) | 2 |
| Индексы | 7 |
| Триггеры | 1 |
| Роли пользователей | 3 |

---

## ИНСТРУКЦИЯ ДЛЯ CLAUDE CODE

Создай все таблицы PostgreSQL строго в порядке из раздела «Порядок создания таблиц».
Используй точные типы данных, ограничения CHECK и FK из этого файла.
COMMENT ON TABLE и COMMENT ON COLUMN уже написаны в каждом блоке — включи их в скрипт.
После таблиц создай триггер check_weights_sum для evaluation_category.
После триггера создай все индексы.
После индексов создай оба представления VIEW.
Весь скрипт должен быть идемпотентным: IF NOT EXISTS, CREATE OR REPLACE.
