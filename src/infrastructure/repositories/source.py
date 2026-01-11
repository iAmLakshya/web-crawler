from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse
from uuid import UUID

from supabase import Client

from src.domain.models import CrawlSource, CrawlSourceCreate, SourceStatus


class SupabaseSourceRepository:
    def __init__(self, client: Client):
        self.client = client
        self.table = client.table("crawl_sources")

    def create(self, source: CrawlSourceCreate) -> CrawlSource:
        data = source.model_dump(mode="json")
        data["domain"] = urlparse(str(source.entry_url)).netloc
        result = self.table.insert(data).execute()
        return CrawlSource.model_validate(result.data[0])

    def get_by_id(self, id: UUID) -> CrawlSource | None:
        result = self.table.select("*").eq("id", str(id)).execute()
        if not result.data:
            return None
        return CrawlSource.model_validate(result.data[0])

    def list(self, status: SourceStatus | None = None) -> list[CrawlSource]:
        query = self.table.select("*")
        if status:
            query = query.eq("status", status)
        result = query.execute()
        return [CrawlSource.model_validate(row) for row in result.data]

    def update_status(self, id: UUID, status: SourceStatus) -> CrawlSource:
        result = self.table.update({"status": status}).eq("id", str(id)).execute()
        return CrawlSource.model_validate(result.data[0])

    def update_next_run(self, id: UUID, next_run_at: datetime) -> CrawlSource:
        result = (
            self.table.update({"next_run_at": next_run_at.isoformat()})
            .eq("id", str(id))
            .execute()
        )
        return CrawlSource.model_validate(result.data[0])

    def delete(self, id: UUID) -> None:
        self.table.delete().eq("id", str(id)).execute()

    def get_due_sources(self) -> list[CrawlSource]:
        result = (
            self.table.select("*")
            .eq("status", "active")
            .lte("next_run_at", datetime.now().isoformat())
            .execute()
        )
        return [CrawlSource.model_validate(row) for row in result.data]
