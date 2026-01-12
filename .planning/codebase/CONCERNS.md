# Codebase Concerns

**Analysis Date:** 2026-01-12

## Tech Debt

**Database operations without error handling:**
- Issue: All `.execute()` calls lack try-catch blocks
- Files:
  - `src/infrastructure/repositories/page.py` (30+ execute calls)
  - `src/infrastructure/repositories/queue.py` (8 execute calls)
  - `src/infrastructure/repositories/run.py` (8 execute calls)
  - `src/infrastructure/repositories/source.py` (7 execute calls)
- Why: Rapid development, assumed stable database connection
- Impact: Network timeouts, connection pool exhaustion, or constraint violations propagate unhandled
- Fix approach: Add try-catch wrappers with specific exception handling and retry logic

**Overly broad exception catching:**
- Issue: `except Exception:` catches all errors silently
- Files:
  - `src/ingestion/crawling/robots.py` (line ~40): Returns `True` silently on robots.txt failures
  - `src/ingestion/crawling/link_extractor.py` (line ~23): Returns empty list on extraction failures
- Why: Defensive coding to prevent crashes
- Impact: Can't distinguish benign failures from real errors; statistics become unreliable
- Fix approach: Catch specific exceptions, log appropriately, track failures separately

**Large complex function:**
- Issue: `CrawlUseCase.start_run()` is ~120 lines with multiple responsibilities
- File: `src/ingestion/use_cases/crawl.py`
- Why: Organic growth during development
- Impact: Hard to test, understand, and modify; race conditions possible
- Fix approach: Extract into smaller methods: `_setup_robots()`, `_seed_queue()`, `_process_batch()`

## Known Bugs

**No known bugs documented**
- Codebase is relatively new
- No issue tracker integration detected

## Security Considerations

**No SSRF protection:**
- Risk: CLI accepts any URL without validation; could crawl internal networks, file:// URLs
- File: `src/interfaces/cli/crawl.py` (line ~22)
- Current mitigation: None
- Recommendations: Add URL validation, blocklist for private IP ranges and non-HTTP schemes

**Hardcoded User-Agent rotation:**
- Risk: Designed to appear as different browsers; may violate ToS of target sites
- File: `src/ingestion/crawling/http_client.py` (lines 12-18)
- Current mitigation: Respects robots.txt
- Recommendations: Add option for honest User-Agent, document usage policy

**No content sanitization:**
- Risk: Raw HTML stored without sanitization; potential XSS if displayed later
- File: `src/domain/models/page.py` (content field)
- Current mitigation: Content only stored, not rendered
- Recommendations: Add sanitization if content is ever displayed

**Service key exposure risk:**
- Risk: Using Supabase service key (elevated privileges) instead of anon key
- File: `src/infrastructure/config.py`
- Current mitigation: `.env` file gitignored
- Recommendations: Document key management, consider row-level security

## Performance Bottlenecks

**Unbounded content storage:**
- Problem: `content: str | None` in `CrawledPage` has no max length
- File: `src/domain/models/page.py`
- Measurement: Pages can be >1MB each
- Cause: No compression or truncation
- Improvement path: Add content size limits, consider compression before storage

**In-memory URL deduplication:**
- Problem: Builds full `seen_hashes` set for sitemap seeding
- File: `src/ingestion/use_cases/crawl.py` (lines ~155-164)
- Measurement: 100k URLs = ~8MB memory
- Cause: Simple implementation for correctness
- Improvement path: Use streaming/pagination or database-based deduplication

**Sequential batch inserts:**
- Problem: Each `create_batch()` is a network round-trip
- File: `src/ingestion/use_cases/crawl.py`
- Measurement: Network latency per batch
- Cause: Supabase client doesn't support multi-statement transactions easily
- Improvement path: Batch larger chunks, use database-side batching

## Fragile Areas

**Rate limiter lock pattern:**
- File: `src/ingestion/crawling/rate_limiter.py` (lines 61-65)
- Why fragile: Manual lock release during sleep; if interrupted, state is inconsistent
- Common failures: Exception during sleep leaves lock in wrong state
- Safe modification: Use context manager pattern
- Test coverage: None

**Global Supabase client singleton:**
- File: `src/infrastructure/db/supabase.py`
- Why fragile: Single `global _client` with no thread-safety or re-initialization protection
- Common failures: Partial initialization, connection pool exhaustion
- Safe modification: Consider connection pooling or per-request clients
- Test coverage: None

## Scaling Limits

**Supabase connection limits:**
- Current capacity: Depends on Supabase plan (free tier has limits)
- Limit: Connection pool exhaustion under high concurrency
- Symptoms at limit: Database connection errors
- Scaling path: Upgrade Supabase plan, add connection pooling

**Memory for large crawls:**
- Current capacity: Limited by system RAM for URL deduplication
- Limit: ~1M URLs before significant memory pressure
- Symptoms at limit: OOM errors, swapping
- Scaling path: Database-backed deduplication, streaming processing

## Dependencies at Risk

**requests library:**
- Risk: Synchronous-only; limits throughput scalability
- Impact: Can't easily migrate to async architecture
- Migration plan: Consider httpx for async support when needed

**Supabase client:**
- Risk: Vendor lock-in to Supabase API
- Impact: Migration to other PostgreSQL providers requires rewrite
- Migration plan: Repository pattern provides abstraction layer; implement alternative adapters

## Missing Critical Features

**No `.env.example` file:**
- Problem: Required environment variables not documented
- Current workaround: Trial and error or reading config.py
- Blocks: Easy onboarding for new developers
- Implementation complexity: Low (create file with placeholders)

**No retry mechanism for HTTP failures:**
- Problem: Transient network errors cause permanent page failures
- Current workaround: Re-run entire crawl
- Blocks: Reliable crawling of flaky sites
- Implementation complexity: Medium (add retry logic to http_client.py)

**No crawl resume capability:**
- Problem: If crawl is interrupted, must restart from beginning
- Current workaround: None
- Blocks: Crawling large sites reliably
- Implementation complexity: Medium (queue already persisted; need checkpoint logic)

## Test Coverage Gaps

**Zero test coverage:**
- What's not tested: Entire codebase
- Risk: Regression bugs, refactoring fear
- Priority: High
- Difficulty to test: Low for pure functions, medium for repositories

**Priority test targets:**
1. `src/domain/rules/url.py` - Pure functions, easy to test, high business value
2. `src/ingestion/crawling/rate_limiter.py` - Thread safety critical path
3. `src/ingestion/use_cases/crawl.py` - Core business logic
4. `src/infrastructure/repositories/*.py` - Data integrity

---

*Concerns audit: 2026-01-12*
*Update as issues are fixed or new ones discovered*
