
exam_tracker_report.sql
Отчет по текущему состоянию проекта Exam Tracker



Таблица пользователей


CREATE TABLE exam_tracker.user
(
user_id Int32,
email String,
first_name String,
last_name String,
middle_name String,
phone_number String,
educational_institution String,
faculty String,
group String,
course String,
created_at DateTime
)
ENGINE = MergeTree
ORDER BY user_id
SETTINGS index_granularity = 8192;



Таблица билетов



CREATE TABLE exam_tracker.ticket
(
ticket_id Int32,
subject String,
max_points Int32,
question_count Int32,
difficulty Int32
)
ENGINE = MergeTree
ORDER BY ticket_id
SETTINGS index_granularity = 8192;


 Таблица попыток


CREATE TABLE exam_tracker.attempt
(
attempt_id Int32,
user_id Int32,
ticket_id Int32,
attempt_number Int32,
score_earned Int32,
score_max Int32,
passing_rate Float32,
attempt_date DateTime,
session_id Int32
)
ENGINE = MergeTree
ORDER BY attempt_id
SETTINGS index_granularity = 8192;


 Kafka-таблица


CREATE TABLE exam_tracker.kafka_events
(
user String,
ticket String,
attempt String
)
ENGINE = Kafka
SETTINGS
kafka_broker_list = ‘kafka:9092’,
kafka_topic_list = ‘my_topic’,
kafka_group_name = ‘clickhouse_group’,
kafka_format = ‘JSONEachRow’;



 Materialized View: user



CREATE MATERIALIZED VIEW exam_tracker.mv_user
TO exam_tracker.user
AS
SELECT
toInt32(JSONExtractString(user, ‘user_id’)) AS user_id,
JSONExtractString(user, ‘email’) AS email,
JSONExtractString(user, ‘first_name’) AS first_name,
JSONExtractString(user, ‘last_name’) AS last_name,
JSONExtractString(user, ‘middle_name’) AS middle_name,
JSONExtractString(user, ‘phone_number’) AS phone_number,
JSONExtractString(user, ‘educational_institution’) AS educational_institution,
JSONExtractString(user, ‘faculty’) AS faculty,
JSONExtractString(user, ‘group’) AS group,
JSONExtractString(user, ‘course’) AS course,
now() AS created_at
FROM exam_tracker.kafka_events;


 Materialized View: ticket



CREATE MATERIALIZED VIEW exam_tracker.mv_ticket
TO exam_tracker.ticket
AS
SELECT
toInt32(JSONExtractString(ticket, ‘ticket_id’)) AS ticket_id,
JSONExtractString(ticket, ‘subject’) AS subject,
JSONExtractInt(ticket, ‘max_points’) AS max_points,
JSONExtractInt(ticket, ‘question_count’) AS question_count,
toInt32(JSONExtractString(ticket, ‘diffuclty’)) AS difficulty
FROM exam_tracker.kafka_events;



Materialized View: attempt



CREATE MATERIALIZED VIEW exam_tracker.mv_attempt
TO exam_tracker.attempt
AS
SELECT
toInt32(JSONExtractString(attempt, ‘attemptId’)) AS attempt_id,
toInt32(JSONExtractString(attempt, ‘userId’)) AS user_id,
toInt32(JSONExtractString(attempt, ‘ticketId’)) AS ticket_id,
JSONExtractInt(attempt, ‘attemptNumber’) AS attempt_number,
JSONExtractInt(attempt, ‘scoreEarned’) AS score_earned,
JSONExtractInt(attempt, ‘maxScore’) AS score_max,
(JSONExtractInt(attempt, ‘scoreEarned’) / JSONExtractInt(attempt, ‘maxScore’)) * 100 AS passing_rate,
parseDateTimeBestEffort(replaceAll(JSONExtractString(attempt, ‘attemptDate’), ‘;’, ’ ’)) AS attempt_date,
toInt32(JSONExtractString(attempt, ‘sessionId’)) AS session_id
FROM exam_tracker.kafka_events;



 Проверка состояния данных



SELECT count() FROM exam_tracker.user;
SELECT count() FROM exam_tracker.ticket;
SELECT count(*) FROM exam_tracker.attempt;



 Текущее состояние проекта



 user: данные поступают корректно.
 ticket: данные пока не загружаются.
 attempt: данные пока не загружаются.
 Основная обнаруженная проблема: некорректные даты
 в поле attemptDate (например, 29.02.2026),
 из-за чего mv_attempt падает с ошибкой
 CANNOT_PARSE_DATETIME.
 Дополнительно была исправлена обработка поля
 diffuclty -> difficulty в mv_ticket.





