import logging
import os
import time
from collections import deque

logger = logging.getLogger(__name__)


class ConsumerLagMonitor:
    def __init__(self, max_samples: int | None = None) -> None:
        self._max_samples = max_samples or int(os.getenv("CONSUMER_LAG_MAX_SAMPLES", "100"))
        self._timestamps: deque[float] = deque(maxlen=self._max_samples)
        self._processed_count = 0

    def observe_message(self, timestamp_ms: int | None) -> None:
        if timestamp_ms is None:
            return
        self._timestamps.append(float(timestamp_ms) / 1000.0)

    def record_processed_message(self) -> None:
        self._processed_count += 1

    @property
    def lag_seconds(self) -> float | None:
        if not self._timestamps:
            return None
        now = time.time()
        return max(0.0, now - self._timestamps[-1])

    @property
    def processed_count(self) -> int:
        return self._processed_count

    def log_status(self) -> None:
        lag = self.lag_seconds
        logger.info("Consumer lag_seconds=%.2f processed_messages=%s", lag if lag is not None else -1, self.processed_count)
