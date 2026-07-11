import asyncio
import json
import os
import random
import sys
import datetime

from aiokafka import AIOKafkaProducer
from faker import Faker

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

fake = Faker("ru_RU")

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
            payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
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
