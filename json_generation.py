import asyncio
import datetime
import json
import os
import random
import sys
from typing import Any

from aiokafka import AIOKafkaProducer
from faker import Faker
from jsonschema import Draft7Validator

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

fake = Faker("ru_RU")

MESSAGE_SCHEMA = {
    "type": "object",
    "required": ["user", "ticket", "attempt"],
    "additionalProperties": False,
    "properties": {
        "user": {
            "type": "object",
            "required": [
                "user_id",
                "email",
                "first_name",
                "last_name",
                "middle_name",
                "phone_number",
                "educational_institution",
                "course",
                "created_at",
            ],
            "additionalProperties": False,
            "properties": {
                "user_id": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "email": {"type": ["string", "null"]},
                "first_name": {"type": ["string", "null"]},
                "last_name": {"type": ["string", "null"]},
                "middle_name": {"type": ["string", "null"]},
                "phone_number": {"type": ["string", "null"]},
                "educational_institution": {"type": ["string", "null"]},
                "course": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "created_at": {"type": ["string", "null"]},
            },
        },
        "ticket": {
            "type": "object",
            "required": ["ticket_id", "subject", "max_points", "question_count", "difficulty"],
            "additionalProperties": False,
            "properties": {
                "ticket_id": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "subject": {"type": ["string", "null"]},
                "max_points": {"type": "integer", "minimum": 0, "maximum": 2147483647},
                "question_count": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "difficulty": {"type": "integer", "minimum": 1, "maximum": 2147483647},
            },
        },
        "attempt": {
            "type": "object",
            "required": [
                "attemptId",
                "userId",
                "ticketId",
                "attemptNumber",
                "scoreEarned",
                "maxScore",
                "attemptDate",
                "sessionId",
            ],
            "additionalProperties": False,
            "properties": {
                "attemptId": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "userId": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "ticketId": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "attemptNumber": {"type": "integer", "minimum": 1, "maximum": 2147483647},
                "scoreEarned": {"type": "integer", "minimum": 0, "maximum": 2147483647},
                "maxScore": {"type": "integer", "minimum": 0, "maximum": 2147483647},
                "attemptDate": {"type": ["string", "null"]},
                "sessionId": {"type": "integer", "minimum": 1, "maximum": 2147483647},
            },
        },
    },
}


class SchemaValidationError(ValueError):
    pass


user_id = 1
institution_array = [
    "IGPT", "IFMB", "IEBP", "IC", "IMM", "IP", "ICMIT", "ITIS",
    "IFMK", "ISPC", "IPE", "AIRSE", "IEFM", "IRHA", "IDSA",
]


def created_at():
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def attempt_date(start_year=2012):
    
    year = random.randint(start_year, datetime.datetime.now().year)
    month = random.randint(1, 12)
    
    # Определяем максимальное количество дней в месяце
    if month == 2:
        # Проверка на високосный год
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_day = 29
        else:
            max_day = 28
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:
        max_day = 31
    
    day = random.randint(1, max_day)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    
    return f"{day:02d}.{month:02d}.{year};{hours:02d}:{minutes:02d}:{seconds:02d}"


def user_dict_generation():
    global user_id
    dic_json = {
        "user_id": int(user_id),
        "email": f"{fake.email()}",
        "first_name": f"{fake.first_name()}",
        "last_name": f"{fake.last_name()}",
        "middle_name": f"{fake.middle_name()}",
        "phone_number": f"{fake.phone_number()}",
        "educational_institution": f"{random.choice(institution_array)}",
        "course": int(random.randint(1, 4)),
        "created_at": f"{created_at()}",
    }

    user_id += 1
    return dic_json


User_dict_array = [user_dict_generation() for _ in range(99)]

ticket_id = 1
university_subjects = [
    "Mathematics",
    "Computer Science",
    "Programming",
    "Statistics",
    "Linear Algebra",
    "English",
    "History",
    "Philosophy",
    "Geography",
    "Education",
    "Physical Education",
    "Sports Science",
]


def ticket_dict_generation():
    global ticket_id
    dic_json = {
        "ticket_id": int(ticket_id),
        "subject": f"{random.choice(university_subjects)}",
        "max_points": 50,
        "question_count": int(random.randint(4, 5)),
        "difficulty": int(random.randint(1, 10)),
    }
    ticket_id += 1
    return dic_json


Ticket_dict_array = [ticket_dict_generation() for _ in range(1)]

session_id = 1


def json_dict_generation():
    global session_id
    user = random.choice(User_dict_array)
    ticket = random.choice(Ticket_dict_array)
    json_dict = {
        "user": user,
        "ticket": ticket,
        "attempt": {
            "attemptId": int(random.randint(1, 20)),
            "userId": int(user["user_id"]),
            "ticketId": int(ticket["ticket_id"]),
            "attemptNumber": int(random.randint(1, 100)),
            "scoreEarned": int(random.randint(1, 50)),
            "maxScore": int(50),
            "attemptDate": attempt_date(),
            "sessionId": int(session_id),
        },
    }
    session_id += 1
    return json_dict


def get_bootstrap_servers():
    if os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
        return os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    kafka_host = os.getenv("KAFKA_HOST", "localhost")
    kafka_port = "9092" if kafka_host == "kafka" else "29092"
    return f"{kafka_host}:{kafka_port}"


def _coerce_int(value: Any, default: int = 0, *, nullable: bool = False) -> int | None:
    if value is None:
        return None if nullable else default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None if nullable else default
        return int(text)
    return default


def _coerce_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return str(int(value))
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


def normalize_message_payload(payload: dict[str, Any]) -> dict[str, Any]:
    user = payload.get("user") or {}
    ticket = payload.get("ticket") or {}
    attempt = payload.get("attempt") or {}

    return {
        "user": {
            "user_id": _coerce_int(user.get("user_id"), default=0),
            "email": _coerce_optional_string(user.get("email")),
            "first_name": _coerce_optional_string(user.get("first_name")),
            "last_name": _coerce_optional_string(user.get("last_name")),
            "middle_name": _coerce_optional_string(user.get("middle_name")),
            "phone_number": _coerce_optional_string(user.get("phone_number")),
            "educational_institution": _coerce_optional_string(user.get("educational_institution")),
            "course": _coerce_int(user.get("course"), default=0),
            "created_at": _coerce_optional_string(user.get("created_at")),
        },
        "ticket": {
            "ticket_id": _coerce_int(ticket.get("ticket_id"), default=0),
            "subject": _coerce_optional_string(ticket.get("subject")),
            "max_points": _coerce_int(ticket.get("max_points"), default=0),
            "question_count": _coerce_int(ticket.get("question_count"), default=0),
            "difficulty": _coerce_int(ticket.get("difficulty"), default=0),
        },
        "attempt": {
            "attemptId": _coerce_int(attempt.get("attemptId"), default=0),
            "userId": _coerce_int(attempt.get("userId"), default=0),
            "ticketId": _coerce_int(attempt.get("ticketId"), default=0),
            "attemptNumber": _coerce_int(attempt.get("attemptNumber"), default=0),
            "scoreEarned": _coerce_int(attempt.get("scoreEarned"), default=0),
            "maxScore": _coerce_int(attempt.get("maxScore"), default=0),
            "attemptDate": _coerce_optional_string(attempt.get("attemptDate")),
            "sessionId": _coerce_int(attempt.get("sessionId"), default=0),
        },
    }


def validate_message_payload(payload: dict[str, Any]) -> None:
    validator = Draft7Validator(MESSAGE_SCHEMA)
    errors = sorted(validator.iter_errors(payload), key=lambda error: error.path)
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, error.path))}: {error.message}" for error in errors
        )
        raise SchemaValidationError(details)


async def send_messages_to_kafka(messages):
    bootstrap_servers = get_bootstrap_servers()
    topic = os.getenv("KAFKA_TOPIC", "json_user_rachive")

    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        client_id="web-producer",
    )

    try:
        await producer.start()
        for message in messages:
            normalized_message = normalize_message_payload(message)
            validate_message_payload(normalized_message)
            payload = json.dumps(normalized_message, ensure_ascii=False).encode("utf-8")
            await producer.send_and_wait(topic=topic, value=payload)
        print(f"Отправлено {len(messages)} сообщений в Kafka ({bootstrap_servers}, topic={topic})")
    except Exception as e:
        print(f"Kafka недоступна ({bootstrap_servers}): {e}")
        print("Сгенерированные данные выведены выше. Запустите Kafka: docker compose up -d kafka")
    finally:
        await producer.stop()


async def main():
    messages = [json_dict_generation() for _ in range(99)]
    for message in messages:
        print(message)
    await send_messages_to_kafka(messages)


if __name__ == "__main__":
    asyncio.run(main())
