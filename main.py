from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
import random
import sys
import time

import requests
from lxml import etree, html

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class Crawler:
    def __init__(self, start_url: str, delay: float = 0.5):
        self.start_url = self._normalize_url(start_url)
        parsed = urlparse(self.start_url)
        self.domain = parsed.netloc
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.delay = delay
        self.seen_urls = set()
        self.queue = deque()
        self.session = requests.Session()

        self.robots = RobotFileParser()
        self._load_robots()
        self._load_sitemaps()

        # Add start URL after sitemap loading
        self._add_url(self.start_url)

    def _random_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def _load_robots(self):
        robots_url = f"{self.base_url}/robots.txt"
        self.robots.set_url(robots_url)
        try:
            response = self.session.get(
                robots_url,
                timeout=10,
                headers={"User-Agent": self._random_user_agent()},
            )
            if response.status_code == 200:
                self.robots.parse(response.text.splitlines())
                delay = self.robots.crawl_delay("*")
                if delay:
                    self.delay = max(self.delay, delay)
                print(f"Loaded robots.txt (crawl-delay: {self.delay}s)")
            else:
                self.robots.parse([]) 
        except Exception:
            self.robots.parse([])
            print("No robots.txt found, allowing all")

    def _load_sitemaps(self):
        sitemap_urls = []
        if self.robots.site_maps():
            sitemap_urls.extend(self.robots.site_maps())
        else:
            sitemap_urls.append(f"{self.base_url}/sitemap.xml")

        for sitemap_url in sitemap_urls:
            self._parse_sitemap(sitemap_url)

        if self.seen_urls:
            print(f"Loaded {len(self.seen_urls)} URLs from sitemaps")

    def _parse_sitemap(self, sitemap_url: str):
        try:
            response = self.session.get(
                sitemap_url,
                timeout=10,
                headers={"User-Agent": self._random_user_agent()},
            )
            if response.status_code != 200:
                return

            root = etree.fromstring(response.content)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Handle sitemap index (nested sitemaps)
            sitemap_refs = root.xpath(
                "//sm:sitemap/sm:loc/text()", namespaces=ns
            ) or root.xpath("//sitemap/loc/text()")
            for ref in sitemap_refs:
                self._parse_sitemap(ref)

            # Extract URLs
            urls = root.xpath(
                "//sm:url/sm:loc/text()", namespaces=ns
            ) or root.xpath("//url/loc/text()")
            for url in urls:
                self._add_url(url)
        except Exception:
            pass

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/") or "/"
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            parsed.query,
            "",
        ))

    def _can_fetch(self, url: str) -> bool:
        try:
            return self.robots.can_fetch("*", url)
        except Exception:
            return True

    def _add_url(self, url: str) -> bool:
        normalized = self._normalize_url(url)
        if urlparse(normalized).netloc != self.domain:
            return False
        if normalized in self.seen_urls:
            return False
        if not self._can_fetch(normalized):
            return False
        self.seen_urls.add(normalized)
        self.queue.append(normalized)
        return True

    def download(self, url: str) -> str | None:
        try:
            response = self.session.get(
                url,
                timeout=10,
                headers={"User-Agent": self._random_user_agent()},
            )
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
        return sum(1 for url in urls if self._add_url(url))

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
