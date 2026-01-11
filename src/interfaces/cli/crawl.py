from __future__ import annotations

import argparse
import logging
import sys
from uuid import UUID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Web crawler CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create source command
    create_parser = subparsers.add_parser("create", help="Create a new crawl source")
    create_parser.add_argument("url", help="Entry URL to crawl")
    create_parser.add_argument(
        "--type",
        choices=["single_page", "full_domain"],
        default="full_domain",
        help="Crawl type",
    )

    # Run crawl command
    run_parser = subparsers.add_parser("run", help="Run a crawl for a source")
    run_parser.add_argument("source_id", type=UUID, help="Source ID to crawl")
    run_parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests")
    run_parser.add_argument("--batch-size", type=int, default=10, help="Batch size for queue")

    args = parser.parse_args()

    # Import here to avoid circular imports and delay loading
    from src.infrastructure.db import get_supabase_client
    from src.infrastructure.repositories import (
        SupabaseCrawledPageRepository,
        SupabaseQueueRepository,
        SupabaseRunRepository,
        SupabaseSourceRepository,
    )
    from src.ingestion.crawling import HttpClient
    from src.ingestion.use_cases import CrawlUseCase

    # Wire dependencies
    client = get_supabase_client()
    source_repo = SupabaseSourceRepository(client)
    run_repo = SupabaseRunRepository(client)
    page_repo = SupabaseCrawledPageRepository(client)
    queue_repo = SupabaseQueueRepository(client)
    http_client = HttpClient()

    use_case = CrawlUseCase(
        source_repo=source_repo,
        run_repo=run_repo,
        page_repo=page_repo,
        queue_repo=queue_repo,
        http_client=http_client,
        delay=getattr(args, "delay", 0.5),
        batch_size=getattr(args, "batch_size", 10),
    )

    if args.command == "create":
        use_case.create_source(args.url, args.type)

    elif args.command == "run":
        result = use_case.start_run(args.source_id)
        logger.info(f"Result: {result.pages_crawled} crawled, {result.pages_failed} failed")


if __name__ == "__main__":
    main()
