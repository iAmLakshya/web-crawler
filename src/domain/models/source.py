from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

SourceType = Literal["single_page", "full_domain"]
SourceStatus = Literal["active", "paused"]


class CrawlSourceCreate(BaseModel):
    domain: str
    entry_url: HttpUrl
    type: SourceType
    frequency: str = "once"
    max_pages: int | None = Field(default=None, gt=0)


class CrawlSource(CrawlSourceCreate):
    id: UUID
    status: SourceStatus = "active"
    created_at: datetime
    next_run_at: datetime | None = None

    model_config = {"from_attributes": True}
