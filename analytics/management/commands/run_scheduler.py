import asyncio
import logging

from django.core.management.base import BaseCommand

from analytics.scheduler import ScheduledRunner

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run the scheduled transformation loop"

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        logger.info("Starting scheduler")
        runner = ScheduledRunner()
        try:
            asyncio.run(runner.run())
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
