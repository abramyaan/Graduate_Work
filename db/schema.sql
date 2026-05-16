-- ПИС «Интеллектуальная оценка резюме на соответствие вакансии»
-- Схема БД PostgreSQL 14+
-- Кодировка: UTF-8
-- Нормальная форма: 3НФ
-- Всего таблиц: 18

-- =============================================================================
-- 1. user_role — Роли пользователей (справочник)
-- =============================================================================

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
('Оператор',      'Operator')
ON CONFLICT (role_name) DO NOTHING;

-- =============================================================================
-- 2. user_account — Пользователи системы (сотрудники)
-- =============================================================================

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

-- =============================================================================
-- 3. candidate — Кандидаты (внешние лица, не пользователи системы)
-- =============================================================================

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

-- =============================================================================
-- 4. specialization — Специализации (справочник)
-- =============================================================================

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
('HR-менеджер')
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- 5. vacancy — Вакансии
-- =============================================================================

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

-- =============================================================================
-- 6. skill — Навыки (справочник)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.skill (
    skill_id SERIAL PRIMARY KEY,
    name     VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT check_skill_name CHECK (LENGTH(name) > 0)
);

COMMENT ON TABLE  public.skill IS 'Справочник навыков (технологий, инструментов)';
COMMENT ON COLUMN public.skill.skill_id IS 'Уникальный идентификатор навыка';
COMMENT ON COLUMN public.skill.name     IS 'Название навыка';

-- =============================================================================
-- 7. vacancy_skill — Навыки вакансии (связующая таблица M:M)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.vacancy_skill (
    vacancy_id INTEGER NOT NULL REFERENCES vacancy(vacancy_id),
    skill_id   INTEGER NOT NULL REFERENCES skill(skill_id),
    PRIMARY KEY (vacancy_id, skill_id)
);

COMMENT ON TABLE  public.vacancy_skill IS 'Навыки, требуемые вакансией';
COMMENT ON COLUMN public.vacancy_skill.vacancy_id IS 'Ссылка на вакансию';
COMMENT ON COLUMN public.vacancy_skill.skill_id   IS 'Ссылка на навык';

-- =============================================================================
-- 8. resume — Резюме кандидатов
-- =============================================================================

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

-- =============================================================================
-- 9. resume_vacancy — Подача резюме на вакансию (связующая таблица M:M)
-- =============================================================================

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

-- =============================================================================
-- 10. resume_skill — Навыки резюме (связующая таблица M:M)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.resume_skill (
    resume_id INTEGER NOT NULL REFERENCES resume(resume_id),
    skill_id  INTEGER NOT NULL REFERENCES skill(skill_id),
    PRIMARY KEY (resume_id, skill_id)
);

COMMENT ON TABLE  public.resume_skill IS 'Навыки, указанные в резюме кандидата';
COMMENT ON COLUMN public.resume_skill.resume_id IS 'Ссылка на резюме';
COMMENT ON COLUMN public.resume_skill.skill_id  IS 'Ссылка на навык';

-- =============================================================================
-- 11. evaluation_category — Категории оценки
-- =============================================================================

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
('ATS-совместимость', 0.10)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- 12. model — ML-модели
-- =============================================================================

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

-- =============================================================================
-- 13. model_config — Параметры модели
-- =============================================================================

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

-- =============================================================================
-- 14. recommendation_rule — Правила рекомендаций
-- =============================================================================

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
( 0.00,  49.99, 'Отклонить')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 15. result_evaluation — Результаты оценки
-- =============================================================================

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

-- =============================================================================
-- 16. result_category_score — Детализация оценок по категориям
-- =============================================================================

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

-- =============================================================================
-- 17. training_pair — Датасет для дообучения
-- =============================================================================

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

-- =============================================================================
-- 18. report — История отчётов
-- =============================================================================

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

-- =============================================================================
-- ТРИГГЕРЫ
-- =============================================================================

-- Триггер для контроля суммы весов категорий = 1.00
CREATE OR REPLACE FUNCTION check_weights_sum()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT ROUND(SUM(weight)::NUMERIC, 2) FROM evaluation_category) != 1.00 THEN
        RAISE EXCEPTION 'Сумма весов категорий должна равняться 1.00';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_weights ON evaluation_category;
CREATE TRIGGER trg_check_weights
AFTER INSERT OR UPDATE ON evaluation_category
FOR EACH ROW EXECUTE FUNCTION check_weights_sum();

-- =============================================================================
-- ИНДЕКСЫ
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_resume_candidate ON resume(candidate_id);
CREATE INDEX IF NOT EXISTS idx_rv_vacancy ON resume_vacancy(vacancy_id);
CREATE INDEX IF NOT EXISTS idx_result_resume ON result_evaluation(resume_id);
CREATE INDEX IF NOT EXISTS idx_result_model  ON result_evaluation(model_id);
CREATE INDEX IF NOT EXISTS idx_result_user   ON result_evaluation(user_id);
CREATE INDEX IF NOT EXISTS idx_result_date   ON result_evaluation(analysis_date);
CREATE INDEX IF NOT EXISTS idx_result_score  ON result_evaluation(overall_score DESC);

-- =============================================================================
-- ПРЕДСТАВЛЕНИЯ (VIEWS)
-- =============================================================================

-- Представление: История всех оценок с полными данными
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

COMMENT ON VIEW v_evaluation_history IS 'История всех оценок резюме с информацией о пользователях, кандидатах и вакансиях';

-- Представление: Ранжированный список кандидатов по баллу
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

COMMENT ON VIEW v_ranked_candidates IS 'Ранжированный список кандидатов по убыванию общего балла соответствия';

-- =============================================================================
-- КОНЕЦ СКРИПТА
-- =============================================================================
-- Всего создано:
-- - 18 таблиц
-- - 2 представления (VIEW)
-- - 7 индексов
-- - 1 триггер
-- - 4 справочника с тестовыми данными (user_role, specialization, evaluation_category, recommendation_rule)
