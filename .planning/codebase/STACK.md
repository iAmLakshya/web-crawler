# Technology Stack

**Analysis Date:** 2026-01-12

## Languages

**Primary:**
- Python 3.13 - All application code (`pyproject.toml`, `.python-version`)

**Secondary:**
- None - Pure Python project

## Runtime

**Environment:**
- Python 3.13+ (specified in `pyproject.toml` and `.python-version`)
- No browser runtime (CLI/backend tool only)

**Package Manager:**
- pip (via pyproject.toml)
- Lockfile: None present (uses version ranges in `pyproject.toml`)

## Frameworks

**Core:**
- None (vanilla Python with Clean Architecture)
- Pydantic 2.12+ for data validation and models

**Testing:**
- Not configured (tests directory empty)
- pyright 1.1.408+ for static type checking (dev dependency)

**Build/Dev:**
- ruff 0.14.11+ for linting and formatting (dev dependency)
- pyright 1.1.408+ for type checking

## Key Dependencies

**Critical:**
- pydantic 2.12.5+ - Domain models, data validation (`src/domain/models/`)
- pydantic-settings 2.12.0+ - Environment configuration (`src/infrastructure/config.py`)
- supabase 2.27.1+ - Database client, primary data store (`src/infrastructure/db/supabase.py`)
- requests 2.32.5+ - HTTP client for web crawling (`src/ingestion/crawling/http_client.py`)
- lxml 6.0.2+ - HTML/XML parsing, link extraction (`src/ingestion/crawling/link_extractor.py`, `robots.py`)

**Infrastructure:**
- python-dotenv 1.2.1+ - Environment variable loading from `.env` files

## Configuration

**Environment:**
- `.env` file for credentials (gitignored)
- Required variables: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- Settings managed via Pydantic BaseSettings (`src/infrastructure/config.py`)

**Build:**
- `pyproject.toml` - Project metadata and dependencies
- No additional build configuration (uses pip/setuptools defaults)

## Platform Requirements

**Development:**
- Any platform with Python 3.13+
- No external dependencies (Docker, databases) - uses Supabase cloud

**Production:**
- CLI tool runs locally or on any Python 3.13+ environment
- Connects to Supabase for PostgreSQL storage
- Future: May support HTTP API, workers (interface stubs present)

---

*Stack analysis: 2026-01-12*
*Update after major dependency changes*
