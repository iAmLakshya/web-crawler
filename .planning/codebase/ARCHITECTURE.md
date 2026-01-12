# Architecture

**Analysis Date:** 2026-01-12

## Pattern Overview

**Overall:** Layered Hexagonal Architecture (Clean Architecture / Ports & Adapters) with Domain-Driven Design

**Key Characteristics:**
- Clear separation between domain, application, infrastructure, and interface layers
- Dependency inversion via Protocol-based ports
- Repository pattern for data access abstraction
- Use case pattern for business workflow orchestration
- Manual dependency injection at composition root

## Layers

**Domain Layer:**
- Purpose: Core business logic, models, and validation rules
- Contains: Pydantic models, business rules, abstract port interfaces
- Location: `src/domain/`
- Depends on: Pydantic only (no external dependencies)
- Used by: All other layers

**Application/Use Cases Layer:**
- Purpose: Business workflow orchestration
- Contains: Use case classes coordinating domain logic with infrastructure
- Location: `src/ingestion/use_cases/`
- Depends on: Domain layer, infrastructure ports
- Used by: Interface layer

**Infrastructure Layer:**
- Purpose: External service implementations (database, HTTP)
- Contains: Repository implementations, database clients, configuration
- Location: `src/infrastructure/`
- Depends on: Domain models, external libraries (supabase, requests)
- Used by: Interface layer (for wiring), use cases (via ports)

**Interface Layer:**
- Purpose: Entry points for different interaction modes
- Contains: CLI commands, future HTTP API, workers, webhooks
- Location: `src/interfaces/`
- Depends on: All layers (composition root responsibility)
- Used by: External callers (users, schedulers)

## Data Flow

**CLI Crawl Command:**

1. User runs: `python -m src.main crawl run <source_id>`
2. CLI parses arguments (`src/interfaces/cli/crawl.py`)
3. Composition root wires dependencies (`src/main.py`)
4. `CrawlUseCase.start_run()` orchestrates workflow (`src/ingestion/use_cases/crawl.py`)
5. Domain rules validate/normalize URLs (`src/domain/rules/url.py`)
6. Repositories persist data to Supabase (`src/infrastructure/repositories/`)
7. HTTP client fetches pages with rate limiting (`src/ingestion/crawling/`)
8. Results logged to console, stats updated in database

**State Management:**
- File-based queue in Supabase (no in-memory state between runs)
- Each crawl run is independent
- Queue items have atomic claiming via RPC functions

## Key Abstractions

**Ports (Interfaces):**
- Purpose: Abstract contracts for external dependencies
- Examples: `CrawledPageRepository`, `QueueRepository`, `SourceRepository`, `RunRepository`
- Location: `src/domain/ports/`
- Pattern: Python Protocol classes

**Repositories (Adapters):**
- Purpose: Implement ports for specific external services
- Examples: `SupabaseCrawledPageRepository`, `SupabaseQueueRepository`
- Location: `src/infrastructure/repositories/`
- Pattern: Class implementing Protocol, injected via constructor

**Use Cases:**
- Purpose: Encapsulate business workflows
- Examples: `CrawlUseCase` with `create_source()`, `start_run()`
- Location: `src/ingestion/use_cases/`
- Pattern: Class with dependencies injected via constructor

**Domain Models:**
- Purpose: Type-safe data structures for business entities
- Examples: `CrawlSource`, `CrawlRun`, `CrawledPage`, `QueueItem`
- Location: `src/domain/models/`
- Pattern: Pydantic BaseModel with `*Create` variants for input

## Entry Points

**Composition Root:**
- Location: `src/main.py`
- Triggers: `python -m src.main <interface> [args]`
- Responsibilities: Wire dependencies, select and start interface

**CLI Interface:**
- Location: `src/interfaces/cli/crawl.py`
- Triggers: `python -m src.main crawl <command> [args]`
- Commands:
  - `create <url> [--type]` - Create new crawl source
  - `run <source_id> [--delay] [--batch-size] [--concurrency] [--max-depth] [--max-pages]` - Execute crawl

**Reserved Interfaces:**
- `src/interfaces/http/` - Future HTTP API (FastAPI/Flask)
- `src/interfaces/workers/` - Future background workers
- `src/interfaces/webhooks/` - Future external callbacks

## Error Handling

**Strategy:** Exceptions bubble up to interface layer, logged and reported

**Patterns:**
- Domain validates input, raises `ValueError` on invalid data
- Repositories execute queries without explicit error handling (gap)
- Use cases catch specific exceptions, update run status on failure
- CLI catches exceptions, prints error, exits with status code

## Cross-Cutting Concerns

**Logging:**
- Python logging module
- Configured in use cases with timestamp + level format
- Console output only (no file or external logging)

**Validation:**
- Pydantic models for structural validation
- Domain rules (`src/domain/rules/url.py`) for business validation
- URL normalization, hashing, domain extraction

**Rate Limiting:**
- `DomainRateLimiter` class (`src/ingestion/crawling/rate_limiter.py`)
- Per-domain delays, respects robots.txt crawl-delay
- Thread-safe with lock-based coordination

**Concurrency:**
- ThreadPoolExecutor for concurrent HTTP requests
- Thread-local session management in HTTP client
- Batch processing in crawl workflow

---

*Architecture analysis: 2026-01-12*
*Update when major patterns change*
