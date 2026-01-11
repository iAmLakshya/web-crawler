from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import CrawlRun, CrawlRunCreate, RunStatus


class RunRepository(Protocol):
    def create(self, run: CrawlRunCreate) -> CrawlRun: ...

    def get_by_id(self, id: UUID) -> CrawlRun | None: ...

    def list_by_source(self, source_id: UUID) -> list[CrawlRun]: ...

    def update_status(self, id: UUID, status: RunStatus) -> CrawlRun: ...

    def update_stats(
        self,
        id: UUID,
        pages_found: int,
        pages_crawled: int,
        pages_failed: int,
    ) -> CrawlRun: ...

    def mark_started(self, id: UUID) -> CrawlRun: ...

    def mark_completed(self, id: UUID, error: str | None = None) -> CrawlRun: ...
