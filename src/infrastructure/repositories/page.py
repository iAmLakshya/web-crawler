from __future__ import annotations

from uuid import UUID

from supabase import Client

from src.domain.models import (
    CrawledPage,
    CrawledPageCreate,
    ParsedPage,
    ParsedPageCreate,
)


class SupabaseCrawledPageRepository:
    def __init__(self, client: Client):
        self.client = client
        self.table = client.table("crawled_pages")

    def create(self, page: CrawledPageCreate) -> CrawledPage:
        data = page.model_dump(mode="json")
        result = self.table.insert(data).execute()
        return CrawledPage.model_validate(result.data[0])

    def create_batch(self, pages: list[CrawledPageCreate]) -> list[CrawledPage]:
        if not pages:
            return []
        data = [page.model_dump(mode="json") for page in pages]
        result = self.table.insert(data).execute()
        return [CrawledPage.model_validate(row) for row in result.data]

    def get_by_id(self, id: UUID) -> CrawledPage | None:
        result = self.table.select("*").eq("id", str(id)).execute()
        if not result.data:
            return None
        return CrawledPage.model_validate(result.data[0])

    def list_by_run(self, run_id: UUID) -> list[CrawledPage]:
        result = (
            self.table.select("*")
            .eq("run_id", str(run_id))
            .order("crawled_at", desc=True)
            .execute()
        )
        return [CrawledPage.model_validate(row) for row in result.data]

    def get_latest_by_url(self, source_id: UUID, url_hash: str) -> CrawledPage | None:
        result = (
            self.table.select("*")
            .eq("source_id", str(source_id))
            .eq("url_hash", url_hash)
            .order("crawled_at", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return CrawledPage.model_validate(result.data[0])


class SupabaseParsedPageRepository:
    def __init__(self, client: Client):
        self.client = client
        self.table = client.table("parsed_pages")
        self.crawled_table = client.table("crawled_pages")

    def create(self, page: ParsedPageCreate) -> ParsedPage:
        data = page.model_dump(mode="json")
        result = self.table.insert(data).execute()
        return ParsedPage.model_validate(result.data[0])

    def get_by_page_id(self, page_id: UUID) -> ParsedPage | None:
        result = self.table.select("*").eq("page_id", str(page_id)).execute()
        if not result.data:
            return None
        return ParsedPage.model_validate(result.data[0])

    def upsert(self, page: ParsedPageCreate) -> ParsedPage:
        data = page.model_dump(mode="json")
        result = self.table.upsert(data, on_conflict="page_id").execute()
        return ParsedPage.model_validate(result.data[0])

    def list_unparsed(self, limit: int = 100) -> list[CrawledPage]:
        # Get crawled pages that don't have a parsed_pages entry
        result = self.client.rpc(
            "get_unparsed_pages",
            {"p_limit": limit},
        ).execute()
        return [CrawledPage.model_validate(row) for row in result.data]
