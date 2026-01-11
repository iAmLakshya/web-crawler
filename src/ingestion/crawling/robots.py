from __future__ import annotations

import logging
from urllib.robotparser import RobotFileParser

from lxml import etree

from src.ingestion.crawling.http_client import HttpClient

logger = logging.getLogger(__name__)


class RobotsHandler:
    def __init__(self, base_url: str, http_client: HttpClient):
        self.base_url = base_url
        self.http_client = http_client
        self.parser = RobotFileParser()
        self.crawl_delay: float | None = None
        self._load()

    def _load(self):
        robots_url = f"{self.base_url}/robots.txt"
        self.parser.set_url(robots_url)
        try:
            content, status_code, _ = self.http_client.download(robots_url)
            if status_code == 200 and content:
                self.parser.parse(content.splitlines())
                self.crawl_delay = self.parser.crawl_delay("*")
                logger.info(f"Loaded robots.txt (crawl-delay: {self.crawl_delay})")
            else:
                self.parser.parse([])
                logger.debug("No robots.txt found")
        except Exception as e:
            self.parser.parse([])
            logger.debug(f"Failed to load robots.txt: {e}")

    def can_fetch(self, url: str) -> bool:
        try:
            return self.parser.can_fetch("*", url)
        except Exception:
            return True

    def get_sitemaps(self) -> list[str]:
        sitemaps = self.parser.site_maps()
        if sitemaps:
            return list(sitemaps)
        return [f"{self.base_url}/sitemap.xml"]


class SitemapParser:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def parse(self, sitemap_url: str) -> list[str]:
        urls: list[str] = []
        visited: set[str] = set()
        self._parse_recursive(sitemap_url, urls, visited, depth=0)
        return urls

    def _parse_recursive(
        self, sitemap_url: str, urls: list[str], visited: set[str], depth: int, max_depth: int = 10
    ):
        if sitemap_url in visited:
            return
        visited.add(sitemap_url)

        if depth >= max_depth:
            logger.warning(f"Max sitemap depth ({max_depth}) reached at: {sitemap_url}")
            return

        try:
            content, status_code, _ = self.http_client.download(sitemap_url)
            if status_code != 200 or not content:
                return

            root = etree.fromstring(content.encode('utf-8', errors='replace'))
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            # Handle sitemap index (nested sitemaps)
            sitemap_refs = root.xpath(
                "//sm:sitemap/sm:loc/text()", namespaces=ns
            ) or root.xpath("//sitemap/loc/text()")
            for ref in sitemap_refs:
                self._parse_recursive(ref, urls, visited, depth + 1, max_depth)

            # Extract URLs
            found_urls = root.xpath(
                "//sm:url/sm:loc/text()", namespaces=ns
            ) or root.xpath("//url/loc/text()")
            urls.extend(found_urls)
        except Exception as e:
            logger.warning(f"Failed to parse sitemap {sitemap_url}: {e}")
