from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse
import sys
import time

import requests
from lxml import html


class Crawler:
    def __init__(self, start_url: str, delay: float = 0.5):
        self.start_url = self._normalize_url(start_url)
        self.domain = urlparse(self.start_url).netloc
        self.delay = delay
        self.seen_urls = set()
        self.queue = deque([self.start_url])
        self.seen_urls.add(self.start_url)

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/") or "/"
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            parsed.query,
            "",  # strip fragment
        ))

    def download(self, url: str) -> str | None:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_links(self, content: str, base_url: str) -> list[str]:
        try:
            tree = html.fromstring(content)
            hrefs = tree.xpath("//a/@href")
            return [urljoin(base_url, href) for href in hrefs]
        except Exception:
            return []

    def add_urls(self, urls: list[str]) -> int:
        count = 0
        for url in urls:
            normalized = self._normalize_url(url)
            if urlparse(normalized).netloc != self.domain:
                continue
            if normalized in self.seen_urls:
                continue
            self.seen_urls.add(normalized)
            self.queue.append(normalized)
            count += 1
        return count

    def run(self):
        while self.queue:
            url = self.queue.popleft()
            content = self.download(url)
            if content is None:
                continue
            links = self.extract_links(content, url)
            added = self.add_urls(links)
            print({
                "current": url,
                "queue_len": len(self.queue),
                "new_urls": added,
            })
            if self.queue:
                time.sleep(self.delay)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <start_url>")
        sys.exit(1)

    crawler = Crawler(sys.argv[1])
    crawler.run()
