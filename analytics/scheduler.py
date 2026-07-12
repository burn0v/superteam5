import asyncio
import logging
import os
import time
from datetime import datetime

from analytics.kafka_consumer import consume_kafka_messages

logger = logging.getLogger(__name__)


class ScheduledRunner:
    def __init__(self, interval_seconds: int | None = None) -> None:
        self.interval_seconds = interval_seconds or int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "60"))
        self._running = False

    async def run(self) -> None:
        self._running = True
        logger.info("Scheduler started with interval=%s seconds", self.interval_seconds)
        while self._running:
            start = time.time()
            try:
                await self._tick()
            except Exception as exc:
                logger.exception("Scheduler tick failed: %s", exc)

            elapsed = time.time() - start
            sleep_for = max(0, self.interval_seconds - elapsed)
            if sleep_for:
                await asyncio.sleep(sleep_for)

    async def _tick(self) -> None:
        logger.info("Scheduler tick at %s", datetime.utcnow().isoformat())

    async def stop(self) -> None:
        self._running = False


async def run_scheduler_once() -> None:
    runner = ScheduledRunner()
    await runner.run()


if __name__ == "__main__":
    asyncio.run(run_scheduler_once())
