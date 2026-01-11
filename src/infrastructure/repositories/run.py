from __future__ import annotations

from datetime import datetime
from uuid import UUID

from supabase import Client

from src.domain.models import CrawlRun, CrawlRunCreate, RunStatus


class SupabaseRunRepository:
    def __init__(self, client: Client):
        self.client = client
        self.table = client.table("crawl_runs")

    def create(self, run: CrawlRunCreate) -> CrawlRun:
        data = run.model_dump(mode="json")
        result = self.table.insert(data).execute()
        return CrawlRun.model_validate(result.data[0])

    def get_by_id(self, id: UUID) -> CrawlRun | None:
        result = self.table.select("*").eq("id", str(id)).execute()
        if not result.data:
            return None
        return CrawlRun.model_validate(result.data[0])

    def list_by_source(self, source_id: UUID) -> list[CrawlRun]:
        result = (
            self.table.select("*")
            .eq("source_id", str(source_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [CrawlRun.model_validate(row) for row in result.data]

    def update_status(self, id: UUID, status: RunStatus) -> CrawlRun:
        result = self.table.update({"status": status}).eq("id", str(id)).execute()
        return CrawlRun.model_validate(result.data[0])

    def update_stats(
        self,
        id: UUID,
        pages_found: int,
        pages_crawled: int,
        pages_failed: int,
    ) -> CrawlRun:
        result = (
            self.table.update({
                "pages_found": pages_found,
                "pages_crawled": pages_crawled,
                "pages_failed": pages_failed,
            })
            .eq("id", str(id))
            .execute()
        )
        return CrawlRun.model_validate(result.data[0])

    def mark_started(self, id: UUID) -> CrawlRun:
        result = (
            self.table.update({
                "status": "running",
                "started_at": datetime.now().isoformat(),
            })
            .eq("id", str(id))
            .execute()
        )
        return CrawlRun.model_validate(result.data[0])

    def mark_completed(self, id: UUID, error: str | None = None) -> CrawlRun:
        status = "failed" if error else "completed"
        result = (
            self.table.update({
                "status": status,
                "completed_at": datetime.now().isoformat(),
                "error": error,
            })
            .eq("id", str(id))
            .execute()
        )
        return CrawlRun.model_validate(result.data[0])
