# Test Running Guide

## Test Types

### Integration Tests (in `tests/`)
- **Purpose**: Test full API endpoints with real database
- **Dependencies**: MongoDB (uses test database `lifepilot_test_db`)
- **Location**: `tests/test_api_*.py`, `tests/test_services.py`
- **Marker**: `@pytest.mark.integration`
- **Run**: `pytest tests/ -v -m integration`

### Unit Tests (in `tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Dependencies**: None (all mocked)
- **Location**: `tests/unit/`
- **Marker**: `@pytest.mark.unit`
- **Run**: `pytest tests/unit/ -v -m unit`

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Unit Tests Only (No DB, No Internet, No External APIs)
```bash
pytest -v -m unit
```

### Integration Tests Only (Requires MongoDB)
```bash
pytest -v -m integration
```

### Specific Test File
```bash
pytest tests/unit/test_services_unit.py -v
pytest tests/test_api_tasks.py -v
```

### With Coverage Report
```bash
pytest tests/ -v --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage
```

### Skip Slow Tests
```bash
pytest tests/ -v -m "not slow"
```

## Test Markers
- `@pytest.mark.unit` - Pure unit tests (no external dependencies)
- `@pytest.mark.integration` - Integration tests (requires test DB)
- `@pytest.mark.slow` - Slow running tests

## Test Database
- Integration tests use a separate test database: `lifepilot_test_db`
- Database is automatically created and cleaned up
- Each test gets a fresh database state via fixtures

## Notes
- **Unit tests**: Use mocks for all external dependencies (DB, APIs, internet)
- **Integration tests**: Use real test database but isolated from production
- Both test types are valuable and serve different purposes

