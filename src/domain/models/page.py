from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CrawledPageCreate(BaseModel):
    run_id: UUID
    source_id: UUID
    url: str
    url_hash: str
    content_hash: str | None = None
    content: str | None = None
    status_code: int | None = None
    error: str | None = None


class CrawledPage(CrawledPageCreate):
    id: UUID
    crawled_at: datetime

    model_config = {"from_attributes": True}


class ParsedPageCreate(BaseModel):
    page_id: UUID
    title: str | None = None
    description: str | None = None
    markdown: str | None = None
    metadata: dict[str, Any] | None = None
    word_count: int | None = Field(default=None, ge=0)
    parser_version: str = "1.0"


class ParsedPage(ParsedPageCreate):
    id: UUID
    parsed_at: datetime

    model_config = {"from_attributes": True}
