from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass

from src.domain.models import (
    CrawlRunCreate,
    CrawlSourceCreate,
    CrawledPageCreate,
    QueueItemCreate,
)
from src.domain.ports import (
    CrawledPageRepository,
    QueueRepository,
    RunRepository,
    SourceRepository,
)
from src.domain.rules import extract_domain, get_base_url, normalize_url, url_hash
from src.ingestion.crawling import (
    HttpClient,
    RobotsHandler,
    SitemapParser,
    extract_links,
)

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    pages_crawled: int
    pages_failed: int


class CrawlUseCase:
    def __init__(
        self,
        source_repo: SourceRepository,
        run_repo: RunRepository,
        page_repo: CrawledPageRepository,
        queue_repo: QueueRepository,
        http_client: HttpClient,
        worker_id: str = "default",
        delay: float = 0.5,
        batch_size: int = 10,
        max_depth: int = 10,
        max_pages: int = 1000,
    ):
        self.source_repo = source_repo
        self.run_repo = run_repo
        self.page_repo = page_repo
        self.queue_repo = queue_repo
        self.http_client = http_client
        self.worker_id = worker_id
        self.delay = delay
        self.batch_size = batch_size
        self.max_depth = max_depth
        self.max_pages = max_pages

    def create_source(self, entry_url: str, source_type: str = "full_domain") -> None:
        source = CrawlSourceCreate(
            domain=extract_domain(entry_url),
            entry_url=entry_url,
            type=source_type,
        )
        created = self.source_repo.create(source)
        logger.info(f"Created source: {created.id} for {created.domain}")

    def start_run(self, source_id) -> CrawlResult:
        source = self.source_repo.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        # Create run
        run = self.run_repo.create(CrawlRunCreate(source_id=source.id))
        self.run_repo.mark_started(run.id)
        logger.info(f"Started run: {run.id}")

        # Setup robots and sitemap
        base_url = get_base_url(str(source.entry_url))
        robots = RobotsHandler(base_url, self.http_client)
        sitemap_parser = SitemapParser(self.http_client)

        # Respect crawl delay from robots.txt
        effective_delay = self.delay
        if robots.crawl_delay:
            effective_delay = max(self.delay, robots.crawl_delay)

        # Seed queue from sitemaps
        sitemap_urls = []
        for sitemap_url in robots.get_sitemaps():
            sitemap_urls.extend(sitemap_parser.parse(sitemap_url))

        # Add entry URL and sitemap URLs to queue
        urls_to_add = [str(source.entry_url)] + sitemap_urls
        queue_items = []
        seen_hashes = set()

        for url in urls_to_add:
            normalized = normalize_url(url)
            if extract_domain(normalized) != source.domain:
                continue
            if not robots.can_fetch(normalized):
                continue
            h = url_hash(normalized)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            queue_items.append(QueueItemCreate(
                run_id=run.id,
                url=normalized,
                url_hash=h,
            ))

        if queue_items:
            self.queue_repo.add_batch(queue_items)
            logger.info(f"Seeded queue with {len(queue_items)} URLs")

        # Process queue
        pages_crawled = 0
        pages_failed = 0

        while True:
            # Check max pages limit
            if pages_crawled + pages_failed >= self.max_pages:
                logger.info(f"Reached max pages limit ({self.max_pages}), stopping crawl")
                break
            items = self.queue_repo.claim(run.id, self.worker_id, self.batch_size)
            if not items:
                break

            for item in items:
                content, status_code, error = self.http_client.download(item.url)

                # Store page
                content_hash = None
                if content:
                    content_hash = hashlib.sha256(content.encode('utf-8', errors='replace')).hexdigest()

                page = CrawledPageCreate(
                    run_id=run.id,
                    source_id=source.id,
                    url=item.url,
                    url_hash=item.url_hash,
                    content=content,
                    content_hash=content_hash,
                    status_code=status_code,
                    error=error,
                )
                self.page_repo.create(page)

                if status_code and 200 <= status_code < 300 and content:
                    # Extract and queue new links
                    links = extract_links(content, item.url)
                    new_items = []

                    # Check depth limit before adding new items
                    if item.depth + 1 >= self.max_depth:
                        logger.debug(f"Skipping link extraction at depth {item.depth}, max depth ({self.max_depth}) reached")
                    else:
                        for link in links:
                            normalized = normalize_url(link)
                            if extract_domain(normalized) != source.domain:
                                continue
                            if not robots.can_fetch(normalized):
                                continue
                            h = url_hash(normalized)
                            new_items.append(QueueItemCreate(
                                run_id=run.id,
                                url=normalized,
                                url_hash=h,
                                depth=item.depth + 1,
                            ))

                    # Add new URLs (duplicates handled by upsert)
                    if new_items:
                        added = self.queue_repo.add_batch(new_items)
                        if added:
                            logger.debug(f"Added {len(added)} new URLs to queue")

                    self.queue_repo.complete(item.id)
                    pages_crawled += 1
                    logger.info(f"Crawled {item.url}")
                else:
                    self.queue_repo.fail(item.id, error)
                    pages_failed += 1

                time.sleep(effective_delay)

            # Update run stats
            self.run_repo.update_stats(
                run.id,
                pages_found=pages_crawled + pages_failed,
                pages_crawled=pages_crawled,
                pages_failed=pages_failed,
            )

        # Mark run complete
        self.run_repo.mark_completed(run.id)
        logger.info(f"Run complete: {pages_crawled} crawled, {pages_failed} failed")

        return CrawlResult(pages_crawled=pages_crawled, pages_failed=pages_failed)
