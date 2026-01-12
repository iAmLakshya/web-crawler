# External Integrations

**Analysis Date:** 2026-01-12

## APIs & External Services

**Payment Processing:**
- Not detected

**Email/SMS:**
- Not detected

**External APIs:**
- Generic HTTP requests to any URL for web crawling
  - Integration method: `requests` library via `src/ingestion/crawling/http_client.py`
  - Auth: None (public web crawling)
  - Rate limits: Per-domain rate limiting via `DomainRateLimiter` (`src/ingestion/crawling/rate_limiter.py`)

## Data Storage

**Databases:**
- Supabase (PostgreSQL Backend-as-a-Service)
  - Connection: Via `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` env vars
  - Client: supabase-py 2.27.1+ (`src/infrastructure/db/supabase.py`)
  - Tables:
    - `crawl_sources` - Source configurations (`src/infrastructure/repositories/source.py`)
    - `crawl_runs` - Crawl execution records (`src/infrastructure/repositories/run.py`)
    - `crawled_pages` - Downloaded page content (`src/infrastructure/repositories/page.py`)
    - `parsed_pages` - Parsed page data (`src/infrastructure/repositories/page.py`)
    - `crawl_queue` - Job queue with atomic claiming (`src/infrastructure/repositories/queue.py`)
  - RPC Functions:
    - `claim_queue_items` - Atomic task claiming with FOR UPDATE SKIP LOCKED
    - `reset_stale_queue_items` - Timeout handling for stale workers
    - `get_unparsed_pages` - Filtering unparsed content

**File Storage:**
- Not detected

**Caching:**
- Not detected (all database queries, no Redis/Memcached)

## Authentication & Identity

**Auth Provider:**
- None (CLI tool, no user authentication)
- Supabase service key used for database access (machine-to-machine)

**OAuth Integrations:**
- Not detected

## Monitoring & Observability

**Error Tracking:**
- Not detected (no Sentry, Datadog, etc.)

**Analytics:**
- Not detected

**Logs:**
- Python logging module to stdout
  - Format: `%(asctime)s [%(levelname)s] %(message)s`
  - Time format: `%H:%M:%S`
  - Configuration: `src/ingestion/use_cases/crawl.py`

## CI/CD & Deployment

**Hosting:**
- Not configured (CLI tool runs locally)

**CI Pipeline:**
- Not detected (no GitHub Actions, GitLab CI, etc.)

## Environment Configuration

**Development:**
- Required env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- Secrets location: `.env` file (gitignored)
- Mock/stub services: None - requires live Supabase connection

**Staging:**
- Not applicable (no staging environment configured)

**Production:**
- Same as development - CLI tool connects to Supabase

## Webhooks & Callbacks

**Incoming:**
- Not detected (webhook interface stub exists at `src/interfaces/webhooks/`)

**Outgoing:**
- Not detected

## Web Standards Compliance

**robots.txt:**
- Full support via `RobotsHandler` (`src/ingestion/crawling/robots.py`)
- Respects crawl-delay directives
- Permission checking before crawling

**sitemap.xml:**
- Full support via `SitemapParser` (`src/ingestion/crawling/robots.py`)
- Recursive sitemap index parsing (max depth: 10)
- Namespace-aware XML extraction

---

*Integration audit: 2026-01-12*
*Update when adding/removing external services*
