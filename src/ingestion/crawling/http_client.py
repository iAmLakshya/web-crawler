from __future__ import annotations

import logging
import random

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
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

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
