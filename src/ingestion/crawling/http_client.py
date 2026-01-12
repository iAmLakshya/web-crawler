from __future__ import annotations

import logging
import random
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
]


class HttpClient:
    def __init__(self, timeout: int = 10, max_workers: int = 10):
        self.timeout = timeout
        self.max_workers = max_workers
        self._local = threading.local()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    @property
    def session(self) -> requests.Session:
        if not hasattr(self._local, 'session'):
            self._local.session = requests.Session()
        return self._local.session

    def _random_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def get(self, url: str) -> requests.Response:
        return self.session.get(
            url,
            timeout=self.timeout,
            headers={"User-Agent": self._random_user_agent()},
        )

    def download(self, url: str) -> tuple[str | None, int | None, str | None]:
        try:
            response = self.get(url)
            response.raise_for_status()
            return response.text, response.status_code, None
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            status_code = e.response.status_code if e.response is not None else None
            return None, status_code, str(e)

    def _download_with_url(self, url: str) -> tuple[str, str | None, int | None, str | None]:
        """Download a URL and return the result with the URL included."""
        content, status_code, error = self.download(url)
        return url, content, status_code, error

    def download_many(self, urls: list[str]) -> list[tuple[str, str | None, int | None, str | None]]:
        """Download multiple URLs concurrently.

        Args:
            urls: List of URLs to download.

        Returns:
            List of tuples: (url, content, status_code, error)
        """
        results = list(self.executor.map(self._download_with_url, urls))
        return results

    def close(self) -> None:
        self.executor.shutdown(wait=True)
        # Thread-local sessions are cleaned up when threads end

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
