from __future__ import annotations

from uuid import UUID

from supabase import Client

from src.domain.models import QueueItem, QueueItemCreate


class SupabaseQueueRepository:
    def __init__(self, client: Client):
        self.client = client
        self.table = client.table("crawl_queue")

    def add(self, item: QueueItemCreate) -> QueueItem:
        data = item.model_dump(mode="json")
        result = self.table.insert(data).execute()
        return QueueItem.model_validate(result.data[0])

    def add_batch(self, items: list[QueueItemCreate]) -> list[QueueItem]:
        if not items:
            return []
        data = [item.model_dump(mode="json") for item in items]
        result = self.table.insert(data).execute()
        return [QueueItem.model_validate(row) for row in result.data]

    def claim(self, run_id: UUID, worker_id: str, limit: int = 10) -> list[QueueItem]:
        # Use RPC for atomic claim with FOR UPDATE SKIP LOCKED
        result = self.client.rpc(
            "claim_queue_items",
            {
                "p_run_id": str(run_id),
                "p_worker_id": worker_id,
                "p_limit": limit,
            },
        ).execute()
        return [QueueItem.model_validate(row) for row in result.data]

    def complete(self, id: UUID) -> QueueItem:
        result = (
            self.table.update({"status": "completed"})
            .eq("id", str(id))
            .execute()
        )
        return QueueItem.model_validate(result.data[0])

    def fail(self, id: UUID, error: str | None = None) -> QueueItem:
        result = (
            self.table.update({"status": "failed"})
            .eq("id", str(id))
            .execute()
        )
        return QueueItem.model_validate(result.data[0])

    def reset_stale(self, timeout_minutes: int = 5) -> int:
        result = self.client.rpc(
            "reset_stale_queue_items",
            {"p_timeout_minutes": timeout_minutes},
        ).execute()
        return result.data or 0

    def get_pending_count(self, run_id: UUID) -> int:
        result = (
            self.table.select("id", count="exact")
            .eq("run_id", str(run_id))
            .eq("status", "pending")
            .execute()
        )
        return result.count or 0
