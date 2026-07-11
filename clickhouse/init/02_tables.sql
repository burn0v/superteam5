-- users: справочник пользователей.
-- ReplacingMergeTree, т.к. один и тот же user_id прилетает в Kafka много раз
-- (генератор выбирает пользователя случайно для каждой попытки).
-- Дедуп идёт по _inserted_at — последняя версия строки "побеждает".
CREATE TABLE IF NOT EXISTS users
(
    user_id                  UInt32,
    email                    String,
    first_name               String,
    last_name                String,
    middle_name              String,
    phone_number             String,
    educational_institution  LowCardinality(String),
    course                   UInt8,
    created_at               String,
    _inserted_at             DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(_inserted_at)
ORDER BY user_id;

-- tickets: справочник билетов. Тоже дедуплицируется по ticket_id.
CREATE TABLE IF NOT EXISTS tickets
(
    ticket_id       UInt32,
    subject         LowCardinality(String),
    max_points      UInt16,
    question_count  UInt8,
    difficulty      UInt8,
    _inserted_at    DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(_inserted_at)
ORDER BY ticket_id;

-- attempts: фактовая таблица (события "попытка сдачи"). Тут дублей быть не
-- должно — каждое сообщение из Kafka это одна попытка, поэтому обычный
-- MergeTree, без Replacing.
CREATE TABLE IF NOT EXISTS attempts
(
    session_id       UInt32,
    attempt_id       UInt32,
    user_id          UInt32,
    ticket_id        UInt32,
    attempt_number   UInt16,
    score_earned     UInt16,
    max_score        UInt16,
    attempt_date     DateTime,
    _inserted_at     DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (attempt_date, session_id);
