from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

QueueStatus = Literal["pending", "processing", "completed", "failed"]


class QueueItemCreate(BaseModel):
    run_id: UUID
    url: str
    url_hash: str
    priority: int = 0
    depth: int = Field(default=0, ge=0)


class QueueItem(QueueItemCreate):
    id: UUID
    status: QueueStatus = "pending"
    worker_id: str | None = None
    claimed_at: datetime | None = None
    attempts: int = Field(default=0, ge=0)
    max_attempts: int = Field(default=3, ge=1)
    created_at: datetime

    model_config = {"from_attributes": True}


class QueueItemClaim(BaseModel):
    id: UUID
    status: Literal["processing"] = "processing"
    worker_id: str
    claimed_at: datetime
    attempts: int
