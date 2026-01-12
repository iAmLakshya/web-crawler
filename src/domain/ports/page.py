from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import (
    CrawledPage,
    CrawledPageCreate,
    ParsedPage,
    ParsedPageCreate,
)


class CrawledPageRepository(Protocol):
    def create(self, page: CrawledPageCreate) -> CrawledPage: ...

    def create_batch(self, pages: list[CrawledPageCreate]) -> list[CrawledPage]: ...

    def get_by_id(self, id: UUID) -> CrawledPage | None: ...

    def list_by_run(self, run_id: UUID) -> list[CrawledPage]: ...

    def get_latest_by_url(self, source_id: UUID, url_hash: str) -> CrawledPage | None: ...


class ParsedPageRepository(Protocol):
    def create(self, page: ParsedPageCreate) -> ParsedPage: ...

    def get_by_page_id(self, page_id: UUID) -> ParsedPage | None: ...

    def upsert(self, page: ParsedPageCreate) -> ParsedPage: ...

    def list_unparsed(self, limit: int = 100) -> list[CrawledPage]: ...
