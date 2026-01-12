# Coding Conventions

**Analysis Date:** 2026-01-12

## Naming Patterns

**Files:**
- snake_case for all Python modules: `http_client.py`, `rate_limiter.py`, `link_extractor.py`
- Single concept per file: `source.py` for source models/repository
- `__init__.py` for package exports with explicit re-exports

**Functions:**
- snake_case for all functions: `create_source()`, `start_run()`, `normalize_url()`
- Private methods with underscore prefix: `_process_item()`, `_download_with_url()`, `_load()`
- Factory functions: `get_*()` pattern: `get_supabase_client()`, `get_settings()`

**Variables:**
- snake_case for variables: `pages_crawled`, `url_hash`, `content_hash`
- UPPER_SNAKE_CASE for constants: `USER_AGENTS` in `http_client.py`
- Private attributes with underscore prefix: `_local`, `_lock`, `_default_delay`

**Types:**
- PascalCase for classes: `HttpClient`, `CrawlUseCase`, `DomainRateLimiter`
- PascalCase for Pydantic models: `CrawlSource`, `CrawledPage`, `QueueItem`
- `*Create` suffix for input models: `CrawlSourceCreate`, `CrawledPageCreate`
- `*Repository` suffix for data access: `SupabaseCrawledPageRepository`
- `*Status` for Literal types: `RunStatus`, `QueueStatus`, `SourceStatus`

## Code Style

**Formatting:**
- Ruff configured for linting/formatting (`pyproject.toml`)
- 4-space indentation (Python standard)
- Double quotes for strings
- No explicit line length limit observed (uses defaults)

**Linting:**
- Ruff 0.14.11+ for linting and formatting
- Pyright 1.1.408+ for static type checking
- No explicit ruff config (uses defaults)

## Import Organization

**Order:**
1. `from __future__ import annotations` (when used)
2. Standard library imports
3. Third-party imports (pydantic, requests, lxml, supabase)
4. Local imports from `src.` package

**Grouping:**
- Blank line between groups
- Multiple imports from same package grouped
- Example from `src/ingestion/use_cases/crawl.py`:
  ```python
  from __future__ import annotations
  import hashlib
  import logging
  from concurrent.futures import ThreadPoolExecutor, as_completed
  from dataclasses import dataclass

  from src.domain.models import CrawlRunCreate, ...
  from src.domain.ports import CrawledPageRepository, ...
  from src.ingestion.crawling import DomainRateLimiter, ...
  ```

**Path Aliases:**
- No aliases configured
- Full paths from `src.` root: `from src.domain.models import ...`

## Error Handling

**Patterns:**
- Raise exceptions with descriptive messages
- `ValueError` for invalid input: `raise ValueError(f"Source {source_id} not found")`
- `RuntimeError` for configuration errors: `raise RuntimeError('SUPABASE_URL ... required')`
- Broad exception catching for external calls (gap - should be more specific)

**Error Types:**
- Standard Python exceptions used (no custom error classes)
- Validation errors from Pydantic models
- HTTP errors via `response.raise_for_status()`

## Logging

**Framework:**
- Python logging module
- Single logger per module: `logger = logging.getLogger(__name__)`

**Patterns:**
- Format: `%(asctime)s [%(levelname)s] %(message)s`
- Time format: `%H:%M:%S`
- Levels: INFO for progress, DEBUG for details, ERROR for failures
- Example: `logger.info(f"Starting crawl run {run.id}")`

## Comments

**When to Comment:**
- Brief inline comments above logic blocks
- Capital letter start, no trailing period required
- Explain "what" for complex flows, not obvious code
- Examples from `src/ingestion/use_cases/crawl.py`:
  - `# Create run`
  - `# Setup robots and sitemap`
  - `# Process queue with concurrency`

**JSDoc/TSDoc:**
- Not applicable (Python project)

**Docstrings:**
- Triple-quoted docstrings for public APIs
- Single-line for simple methods: `"""Process a single queue item."""`
- Multi-line Google-style for complex functions:
  ```python
  """Set a custom delay for a specific domain.

  Args:
      domain: The domain to set the delay for.
      delay: The delay in seconds between requests.
  """
  ```

**TODO Comments:**
- No explicit pattern observed
- No TODO comments found in current codebase

## Function Design

**Size:**
- Prefer smaller functions (most under 30 lines)
- One large function: `start_run()` at ~120 lines (identified as tech debt)

**Parameters:**
- Type hints on all parameters and returns
- Modern union syntax: `str | None` (not `Optional[str]`)
- Default values for optional parameters
- Example: `def download(self, url: str) -> tuple[str | None, int | None, str | None]:`

**Return Values:**
- Explicit return type hints
- Tuple returns for multiple values
- `None` for not-found scenarios (vs raising exception)

## Module Design

**Exports:**
- Explicit exports in `__init__.py` files
- Re-export pattern: `from .crawl import CrawlUseCase, CrawlResult`
- All public classes/functions listed

**Barrel Files:**
- `__init__.py` in every package
- Domain models: `src/domain/models/__init__.py` exports all models
- Ports: `src/domain/ports/__init__.py` exports all protocols

## Type Hints

**Style:**
- Full type hints throughout codebase
- `from __future__ import annotations` for forward references
- Pydantic models for structured data
- Protocol classes for interfaces
- Literal types for enums: `Literal["pending", "processing", "completed", "failed"]`

**Patterns:**
- Generic types: `list[CrawlSource]`, `dict[str, float]`
- Optional: `str | None` (modern syntax)
- Callable: Not heavily used (repository methods are protocol-based)

---

*Convention analysis: 2026-01-12*
*Update when patterns change*
