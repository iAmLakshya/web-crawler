import threading
import time
from typing import Dict


class DomainRateLimiter:
    """Per-domain rate limiter for controlling request frequency."""

    def __init__(self, default_delay: float = 0.5) -> None:
        """Initialize the rate limiter.

        Args:
            default_delay: Default delay in seconds between requests to the same domain.
        """
        self._default_delay = default_delay
        self._domain_delays: Dict[str, float] = {}
        self._last_request_times: Dict[str, float] = {}
        self._lock = threading.Lock()

    def set_delay(self, domain: str, delay: float) -> None:
        """Set a custom delay for a specific domain.

        Args:
            domain: The domain to set the delay for.
            delay: The delay in seconds between requests to this domain.
        """
        with self._lock:
            self._domain_delays[domain] = delay

    def get_delay(self, domain: str) -> float:
        """Get the delay for a specific domain.

        Args:
            domain: The domain to get the delay for.

        Returns:
            The delay in seconds for the specified domain.
        """
        with self._lock:
            return self._domain_delays.get(domain, self._default_delay)

    def acquire(self, domain: str) -> None:
        """Acquire permission to make a request to the specified domain.

        Blocks until enough time has passed since the last request to this domain.

        Args:
            domain: The domain to acquire permission for.
        """
        with self._lock:
            delay = self._domain_delays.get(domain, self._default_delay)
            last_request_time = self._last_request_times.get(domain)

            if last_request_time is not None:
                elapsed = time.monotonic() - last_request_time
                wait_time = delay - elapsed
                if wait_time > 0:
                    # Reserve our slot before releasing the lock
                    self._last_request_times[domain] = time.monotonic() + wait_time
                    # Release lock while sleeping to allow other domains to proceed
                    self._lock.release()
                    try:
                        time.sleep(wait_time)
                    finally:
                        self._lock.acquire()
                    # Update to actual time after waking
                    self._last_request_times[domain] = time.monotonic()
                    return

            self._last_request_times[domain] = time.monotonic()
