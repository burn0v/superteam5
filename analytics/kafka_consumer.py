import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, KafkaError

from analytics.monitoring import ConsumerLagMonitor

from analytics.clickhouse_client import get_clickhouse_client
from json_generation import SchemaValidationError, normalize_message_payload, validate_message_payload

logger = logging.getLogger(__name__)


class ConsumerProcessingError(Exception):
    pass


def _normalize_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace(";", " ")
    try:
        return datetime.strptime(normalized, "%d.%m.%Y %H:%M:%S")
    except ValueError:
        return None


def build_clickhouse_rows(payload: dict) -> dict:
    user = payload.get("user") or {}
    ticket = payload.get("ticket") or {}
    attempt = payload.get("attempt") or {}

    users_row = {
        "user_id": int(user.get("user_id", 0)),
        "email": str(user.get("email", "")),
        "first_name": str(user.get("first_name", "")),
        "last_name": str(user.get("last_name", "")),
        "middle_name": str(user.get("middle_name", "")),
        "phone_number": str(user.get("phone_number", "")),
        "educational_institution": str(user.get("educational_institution", "")),
        "course": int(user.get("course", 0)),
        "created_at": str(user.get("created_at", "")),
    }

    tickets_row = {
        "ticket_id": int(ticket.get("ticket_id", 0)),
        "subject": str(ticket.get("subject", "")),
        "max_points": int(ticket.get("max_points", 0)),
        "question_count": int(ticket.get("question_count", 0)),
        "difficulty": int(ticket.get("difficulty", 0)),
    }

    attempts_row = {
        "session_id": int(attempt.get("sessionId", 0)),
        "attempt_id": int(attempt.get("attemptId", 0)),
        "user_id": int(attempt.get("userId", 0)),
        "ticket_id": int(attempt.get("ticketId", 0)),
        "attempt_number": int(attempt.get("attemptNumber", 0)),
        "score_earned": int(attempt.get("scoreEarned", 0)),
        "max_score": int(attempt.get("maxScore", 0)),
        "attempt_date": _normalize_datetime(attempt.get("attemptDate")),
    }

    return {
        "users": [users_row],
        "tickets": [tickets_row],
        "attempts": [attempts_row],
    }


def get_bootstrap_servers() -> str:
    if os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
        return os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    kafka_host = os.getenv("KAFKA_HOST", "localhost")
    kafka_port = "9092" if kafka_host == "kafka" else "29092"
    return f"{kafka_host}:{kafka_port}"


async def persist_payload(payload: dict) -> None:
    rows = build_clickhouse_rows(payload)
    last_error: Exception | None = None

    for attempt in range(3):
        client = None
        try:
            client = get_clickhouse_client()
            client.insert("users", rows["users"], column_names=list(rows["users"][0].keys()))
            client.insert("tickets", rows["tickets"], column_names=list(rows["tickets"][0].keys()))
            client.insert("attempts", rows["attempts"], column_names=list(rows["attempts"][0].keys()))
            return
        except Exception as exc:
            last_error = exc
            logger.exception("Failed to persist payload into ClickHouse (attempt %s/3)", attempt + 1)
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass

        await asyncio.sleep(2 * (attempt + 1))

    if last_error is not None:
        raise last_error


async def process_message_value(message_value: bytes, *, lag_monitor: ConsumerLagMonitor | None = None) -> bool:
    try:
        payload = json.loads(message_value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        logger.warning("Skipping invalid JSON message: %s", exc)
        return False

    try:
        normalized_payload = normalize_message_payload(payload)
        validate_message_payload(normalized_payload)
        await persist_payload(normalized_payload)
    except SchemaValidationError as exc:
        logger.warning("Skipping message due to schema validation: %s", exc)
        return False
    except Exception as exc:
        logger.exception("Failed to process message: %s", exc)
        raise ConsumerProcessingError(str(exc)) from exc

    if lag_monitor is not None:
        lag_monitor.record_processed_message()

    logger.info("Consumed message")
    return True


async def consume_kafka_messages(stop_event: asyncio.Event | None = None) -> None:
    bootstrap_servers = get_bootstrap_servers()
    topic = os.getenv("KAFKA_TOPIC", "json_user_rachive")
    reconnect_delay = int(os.getenv("KAFKA_RECONNECT_DELAY", "5"))
    lag_monitor = ConsumerLagMonitor()

    while not (stop_event and stop_event.is_set()):
        consumer = None
        try:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=os.getenv("KAFKA_GROUP_ID", "python_consumer_group"),
                auto_offset_reset="earliest",
                enable_auto_commit=False,
            )
            await consumer.start()
            logger.info("Kafka consumer started on %s, topic=%s", bootstrap_servers, topic)

            async for message in consumer:
                try:
                    lag_monitor.observe_message(message.timestamp)
                    processed = await process_message_value(message.value, lag_monitor=lag_monitor)
                    if processed:
                        await consumer.commit()
                        lag_monitor.log_status()
                except KafkaConnectionError as exc:
                    logger.exception("Kafka connection error while consuming message: %s", exc)
                    break
                except KafkaError as exc:
                    logger.exception("Kafka error while consuming message: %s", exc)
                    break
                except ConsumerProcessingError as exc:
                    logger.exception("Consumer processing error: %s", exc)
                    await consumer.commit()
                except Exception as exc:
                    logger.exception("Unexpected consumer error: %s", exc)
                    break
        except asyncio.CancelledError:
            raise
        except KafkaConnectionError as exc:
            logger.exception("Kafka connection lost, retrying in %s seconds: %s", reconnect_delay, exc)
        except KafkaError as exc:
            logger.exception("Kafka error, retrying in %s seconds: %s", reconnect_delay, exc)
        except Exception as exc:
            logger.exception("Kafka consumer loop failed, retrying in %s seconds: %s", reconnect_delay, exc)
        finally:
            if consumer is not None:
                try:
                    await consumer.stop()
                except Exception:
                    pass

        if stop_event and stop_event.is_set():
            break
        await asyncio.sleep(reconnect_delay)


if __name__ == "__main__":
    asyncio.run(consume_kafka_messages())
