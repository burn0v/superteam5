-- Каждое сообщение из kafka_raw выглядит так:
-- {"user": {...}, "ticket": {...}, "attempt": {...}}
--
-- JSONExtract(raw, 'user', 'user_id', 'UInt32') читает вложенный ключ
-- user.user_id и сразу приводит его к нужному типу — в т.ч. если в JSON
-- значение пришло строкой (как attemptId у нас), а не числом. Это и
-- закрывает проблему "нет приведения int'ов" уже на стороне ClickHouse.

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_users TO users AS
SELECT
    JSONExtract(raw, 'user', 'user_id', 'UInt32')                  AS user_id,
    JSONExtract(raw, 'user', 'email', 'String')                    AS email,
    JSONExtract(raw, 'user', 'first_name', 'String')                AS first_name,
    JSONExtract(raw, 'user', 'last_name', 'String')                 AS last_name,
    JSONExtract(raw, 'user', 'middle_name', 'String')               AS middle_name,
    JSONExtract(raw, 'user', 'phone_number', 'String')              AS phone_number,
    JSONExtract(raw, 'user', 'educational_institution', 'String')   AS educational_institution,
    JSONExtract(raw, 'user', 'course', 'UInt8')                     AS course,
    JSONExtract(raw, 'user', 'created_at', 'String')                AS created_at
FROM kafka_raw;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_tickets TO tickets AS
SELECT
    JSONExtract(raw, 'ticket', 'ticket_id', 'UInt32')       AS ticket_id,
    JSONExtract(raw, 'ticket', 'subject', 'String')          AS subject,
    JSONExtract(raw, 'ticket', 'max_points', 'UInt16')       AS max_points,
    JSONExtract(raw, 'ticket', 'question_count', 'UInt8')    AS question_count,
    JSONExtract(raw, 'ticket', 'difficulty', 'UInt8')         AS difficulty
FROM kafka_raw;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_attempts TO attempts AS
SELECT
    JSONExtract(raw, 'attempt', 'sessionId', 'UInt32')       AS session_id,
    JSONExtract(raw, 'attempt', 'attemptId', 'UInt32')       AS attempt_id,
    JSONExtract(raw, 'attempt', 'userId', 'UInt32')          AS user_id,
    JSONExtract(raw, 'attempt', 'ticketId', 'UInt32')        AS ticket_id,
    JSONExtract(raw, 'attempt', 'attemptNumber', 'UInt16')   AS attempt_number,
    JSONExtract(raw, 'attempt', 'scoreEarned', 'UInt16')     AS score_earned,
    JSONExtract(raw, 'attempt', 'maxScore', 'UInt16')        AS max_score,
    parseDateTimeBestEffortOrNull(
        replaceAll(JSONExtract(raw, 'attempt', 'attemptDate', 'String'), ';', ' ')
    )                                                        AS attempt_date
FROM kafka_raw;
