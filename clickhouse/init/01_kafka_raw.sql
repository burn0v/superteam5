-- Таблица-консьюмер: подключается к топику Kafka и читает каждое сообщение
-- как одну строку (JSONAsString). Сама по себе данные не хранит — это "труба".
CREATE TABLE IF NOT EXISTS kafka_raw
(
    raw String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'json_user_rachive',
    kafka_group_name = 'ch_consumer_group',
    kafka_format = 'JSONAsString',
    kafka_num_consumers = 1,
    kafka_skip_broken_messages = 5;
