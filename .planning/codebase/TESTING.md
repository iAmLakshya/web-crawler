# Testing Patterns

**Analysis Date:** 2026-01-12

## Test Framework

**Runner:**
- Not configured (no pytest, unittest, or other framework installed)
- `tests/` directory exists but is empty

**Assertion Library:**
- Not applicable

**Run Commands:**
```bash
# No test commands configured
# Recommended: pip install pytest && pytest tests/
```

## Test File Organization

**Location:**
- `tests/` directory at project root (empty)
- No tests currently written

**Naming:**
- Not established (no test files exist)
- Recommended: `test_*.py` or `*_test.py` (pytest convention)

**Structure:**
```
tests/                          # Currently empty
  (recommended structure)
  ├── domain/
  │   ├── test_models.py       # Model validation tests
  │   └── test_rules.py        # Business rule tests
  ├── ingestion/
  │   ├── test_crawl.py        # CrawlUseCase tests
  │   └── test_http_client.py  # HTTP client tests
  └── infrastructure/
      └── test_repositories.py # Repository integration tests
```

## Test Structure

**Suite Organization:**
- Not established (recommend pytest fixtures and parametrized tests)

**Patterns:**
- Not established

## Mocking

**Framework:**
- Not configured
- Recommended: pytest-mock or unittest.mock

**Patterns:**
- Repository pattern enables easy mocking (Protocol-based interfaces)
- HTTP client can be mocked for unit tests
- Supabase client should be mocked for isolation

**What to Mock:**
- Supabase database calls (all repositories)
- HTTP requests to external sites
- File system operations (if any)
- Time/dates for rate limiter tests

**What NOT to Mock:**
- Domain rules (pure functions, test directly)
- Pydantic model validation (test with real data)
- Business logic in use cases (integration test level)

## Fixtures and Factories

**Test Data:**
- Not established
- Recommended: Factory functions for Pydantic models

```python
# Recommended pattern
def create_test_source(overrides: dict = None) -> CrawlSource:
    defaults = {
        "id": uuid4(),
        "entry_url": "https://example.com",
        "domain": "example.com",
        "crawl_type": "sitemap",
        "status": "active",
        "created_at": datetime.now(),
    }
    return CrawlSource(**(defaults | (overrides or {})))
```

**Location:**
- Recommended: `tests/conftest.py` for shared fixtures
- Recommended: `tests/factories.py` for model factories

## Coverage

**Requirements:**
- No coverage target established
- No coverage tool configured

**Configuration:**
- Recommended: pytest-cov
- Recommended config in `pyproject.toml`:
  ```toml
  [tool.coverage.run]
  source = ["src"]
  omit = ["*/tests/*", "*/__pycache__/*"]
  ```

**View Coverage:**
```bash
# Not configured
# Recommended: pytest --cov=src --cov-report=html
```

## Test Types

**Unit Tests:**
- Not implemented
- Priority targets:
  - `src/domain/rules/url.py` - Pure functions, easy to test
  - `src/ingestion/crawling/rate_limiter.py` - Thread-safe logic
  - `src/domain/models/*.py` - Pydantic validation

**Integration Tests:**
- Not implemented
- Priority targets:
  - `src/ingestion/use_cases/crawl.py` - Full workflow with mocked repos
  - `src/infrastructure/repositories/*.py` - Against test database

**E2E Tests:**
- Not implemented
- Would require test Supabase instance or mocked responses

## Common Patterns

**Async Testing:**
- Not applicable (codebase uses threads, not async/await)
- ThreadPoolExecutor tests need careful synchronization

**Error Testing:**
```python
# Recommended pattern
def test_invalid_source_raises():
    with pytest.raises(ValueError, match="Source .* not found"):
        use_case.start_run(uuid4())
```

**Database Mocking:**
```python
# Recommended pattern with Protocol-based repos
@pytest.fixture
def mock_source_repo():
    repo = Mock(spec=SourceRepository)
    repo.get_by_id.return_value = create_test_source()
    return repo
```

**Snapshot Testing:**
- Not applicable

## Static Analysis

**Type Checking:**
- pyright 1.1.408+ configured as dev dependency
- Run: `pyright src/`
- Full type hints throughout codebase

**Linting:**
- ruff 0.14.11+ configured as dev dependency
- Run: `ruff check src/`
- Run: `ruff format src/`

## Gaps & Recommendations

**Critical Test Gaps:**
1. No unit tests for URL normalization (`src/domain/rules/url.py`)
2. No tests for rate limiter thread safety
3. No tests for CrawlUseCase business logic
4. No integration tests for repositories

**Recommended Test Priority:**
1. `src/domain/rules/url.py` - Low effort, high value
2. `src/ingestion/crawling/rate_limiter.py` - Thread safety critical
3. `src/ingestion/use_cases/crawl.py` - Core business logic
4. `src/infrastructure/repositories/*.py` - Data integrity

---

*Testing analysis: 2026-01-12*
*Update when test patterns change*
