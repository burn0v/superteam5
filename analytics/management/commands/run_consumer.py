import asyncio
import logging

from django.core.management.base import BaseCommand

from analytics.kafka_consumer import consume_kafka_messages

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run the Kafka consumer that writes payloads into ClickHouse"

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        logger.info("Starting Kafka consumer")
        try:
            asyncio.run(consume_kafka_messages())
        except KeyboardInterrupt:
            logger.info("Kafka consumer stopped by user")
