# Codebase Structure

**Analysis Date:** 2026-01-12

## Directory Layout

```
answer-engine/
├── src/                        # Application source code
│   ├── main.py                # Composition root, interface routing
│   ├── domain/                # Core business logic (no external deps)
│   │   ├── models/           # Pydantic domain entities
│   │   ├── ports/            # Abstract interfaces (Protocol classes)
│   │   └── rules/            # Business rules, validation
│   ├── ingestion/             # Data ingestion workflows
│   │   ├── crawling/         # Web crawling mechanics
│   │   └── use_cases/        # Business workflow orchestration
│   ├── infrastructure/        # External service implementations
│   │   ├── config.py         # Settings management
│   │   ├── db/               # Database client setup
│   │   └── repositories/     # Port implementations (adapters)
│   └── interfaces/            # Entry point adapters
│       ├── cli/              # CLI commands
│       ├── http/             # (Reserved) HTTP API
│       ├── workers/          # (Reserved) Background workers
│       └── webhooks/         # (Reserved) External callbacks
├── tests/                      # Test files (currently empty)
├── main.py                     # Root entry point (delegates to src/main)
├── pyproject.toml              # Project metadata & dependencies
├── .python-version             # Python version specification
├── .env                        # Environment variables (gitignored)
├── project-arch.md             # Architecture documentation
└── notes.txt                   # Development notes
```

## Directory Purposes

**src/domain/models/**
- Purpose: Pydantic business models (meaningful core objects)
- Contains: `source.py`, `run.py`, `page.py`, `queue.py`
- Key files: All model files export `*` and `*Create` variants
- Subdirectories: None

**src/domain/ports/**
- Purpose: Abstract interfaces (contracts for external services)
- Contains: Protocol classes defining repository interfaces
- Key files: `source.py`, `run.py`, `page.py`, `queue.py`
- Subdirectories: None

**src/domain/rules/**
- Purpose: Business rules, validation, normalization
- Contains: Pure functions for URL handling
- Key files: `url.py` (normalize_url, url_hash, extract_domain, get_base_url)
- Subdirectories: None

**src/ingestion/crawling/**
- Purpose: Web crawling mechanics (HTTP, robots, parsing)
- Contains: HttpClient, RobotsHandler, SitemapParser, DomainRateLimiter, link_extractor
- Key files:
  - `http_client.py` - Concurrent HTTP downloads with User-Agent rotation
  - `robots.py` - robots.txt and sitemap.xml parsing
  - `link_extractor.py` - HTML link extraction with lxml
  - `rate_limiter.py` - Per-domain rate limiting
- Subdirectories: None

**src/ingestion/use_cases/**
- Purpose: Business workflow orchestration
- Contains: Use case classes coordinating domain + infrastructure
- Key files: `crawl.py` (CrawlUseCase with create_source, start_run)
- Subdirectories: None

**src/infrastructure/db/**
- Purpose: Database client setup
- Contains: Supabase client singleton
- Key files: `supabase.py` (get_supabase_client)
- Subdirectories: None

**src/infrastructure/repositories/**
- Purpose: Port implementations (adapters) for Supabase
- Contains: Repository classes implementing domain ports
- Key files:
  - `source.py` - SupabaseSourceRepository
  - `run.py` - SupabaseRunRepository
  - `page.py` - SupabaseCrawledPageRepository, SupabaseParsedPageRepository
  - `queue.py` - SupabaseQueueRepository
- Subdirectories: None

**src/interfaces/cli/**
- Purpose: CLI command handlers
- Contains: Argparse-based command definitions
- Key files: `crawl.py` (create, run commands)
- Subdirectories: None

## Key File Locations

**Entry Points:**
- `main.py` - Root entry point (delegates to src/main)
- `src/main.py` - Composition root, dependency wiring, interface selection

**Configuration:**
- `pyproject.toml` - Project metadata, dependencies
- `.python-version` - Python 3.13 requirement
- `src/infrastructure/config.py` - Pydantic settings management
- `.env` - Environment variables (SUPABASE_URL, SUPABASE_SERVICE_KEY)

**Core Logic:**
- `src/ingestion/use_cases/crawl.py` - Main crawl orchestration (CrawlUseCase)
- `src/domain/rules/url.py` - URL normalization and business rules
- `src/ingestion/crawling/http_client.py` - HTTP client with concurrency

**Testing:**
- `tests/` - Test directory (currently empty)

**Documentation:**
- `project-arch.md` - Architecture overview
- `notes.txt` - Development notes

## Naming Conventions

**Files:**
- snake_case for all Python modules: `http_client.py`, `rate_limiter.py`
- Single responsibility: one primary class/concept per file
- `__init__.py` for package exports

**Directories:**
- snake_case: `domain/`, `infrastructure/`, `use_cases/`
- Plural for collections: `models/`, `ports/`, `repositories/`

**Special Patterns:**
- `*Create` models for input DTOs: `CrawlSourceCreate`, `CrawledPageCreate`
- `Supabase*Repository` for port implementations
- `*UseCase` for business workflow classes

## Where to Add New Code

**New Feature:**
- Primary code: `src/ingestion/use_cases/` for new workflows
- Domain models: `src/domain/models/`
- Tests: `tests/` (mirroring src structure)

**New Component/Module:**
- Implementation: Feature-appropriate directory in `src/`
- Types: `src/domain/models/` for domain entities
- Tests: `tests/` with matching structure

**New Route/Command:**
- CLI: `src/interfaces/cli/`
- HTTP: `src/interfaces/http/` (future)
- Registration: Update `src/main.py` to wire new interface

**Utilities:**
- Shared helpers: `src/domain/rules/` for business logic
- Infrastructure utilities: `src/infrastructure/`

## Special Directories

**src/processing/**
- Purpose: Reserved for future post-crawl pipelines (enrichment, analytics, ML)
- Source: Not yet implemented
- Committed: Directory may not exist yet

**tests/**
- Purpose: Test files
- Source: Empty (tests not yet written)
- Committed: Yes (placeholder)

**src/interfaces/http/, workers/, webhooks/**
- Purpose: Reserved for future interface implementations
- Source: Stub directories with `__init__.py`
- Committed: Yes (architectural placeholders)

---

*Structure analysis: 2026-01-12*
*Update when directory structure changes*
