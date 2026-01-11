from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

RunStatus = Literal["pending", "running", "completed", "failed"]


class CrawlRunCreate(BaseModel):
    source_id: UUID


class CrawlRun(BaseModel):
    id: UUID
    source_id: UUID
    status: RunStatus = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    pages_found: int = Field(default=0, ge=0)
    pages_crawled: int = Field(default=0, ge=0)
    pages_failed: int = Field(default=0, ge=0)
    error: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
