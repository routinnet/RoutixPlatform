# Routix Platform Test Suite

Comprehensive testing infrastructure for the Routix Platform backend.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── pytest.ini               # Pytest settings
├── test_api_health.py       # Health check tests
├── test_auth.py             # Authentication tests
├── test_templates.py        # Template management tests
├── test_generations.py      # Generation API tests
└── test_services/           # Service layer tests
    ├── test_ai_service.py
    ├── test_storage_service.py
    └── test_embedding_service.py
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=app --cov-report=html
```

### Run specific test types
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Tests requiring AI API keys
pytest -m requires_ai
```

### Run specific test files
```bash
pytest tests/test_api_health.py
pytest tests/test_auth.py -v
```

### Run with different verbosity levels
```bash
# Quiet mode
pytest -q

# Verbose mode
pytest -v

# Extra verbose
pytest -vv
```

## Test Fixtures

Common fixtures available in `conftest.py`:

- `test_session`: Database session for testing
- `test_client`: Synchronous test client
- `async_test_client`: Asynchronous test client
- `test_user`: Pre-created test user
- `test_admin`: Pre-created admin user
- `test_template`: Pre-created template
- `auth_headers`: Authentication headers for test user
- `admin_auth_headers`: Authentication headers for admin

## Writing Tests

### Example Unit Test
```python
import pytest

@pytest.mark.unit
async def test_create_user(test_session):
    # Your test code here
    pass
```

### Example Integration Test
```python
import pytest

@pytest.mark.integration
async def test_full_generation_flow(async_test_client, auth_headers):
    # Your test code here
    pass
```

### Example Test with AI Services
```python
import pytest

@pytest.mark.requires_ai
async def test_ai_generation(async_test_client, auth_headers):
    # Your test code here
    pass
```

## Coverage Requirements

- Minimum coverage: 70%
- Coverage reports: HTML and terminal
- Coverage directory: `htmlcov/`

View coverage report:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

Tests are automatically run in CI/CD pipelines. Ensure all tests pass before merging:

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term

# Check if coverage meets requirements
pytest --cov=app --cov-fail-under=70
```

## Mock Services

For tests that don't require actual AI services, use mocks:

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.unit
async def test_with_mock_ai():
    with patch('app.services.ai_service.VisionAIService') as mock:
        mock.return_value.analyze_template_image = AsyncMock(
            return_value={"style": "modern"}
        )
        # Your test code here
```

## Best Practices

1. Use appropriate markers (`@pytest.mark.unit`, etc.)
2. Keep tests isolated and independent
3. Use fixtures for common setup
4. Mock external services when possible
5. Write descriptive test names
6. Test both success and failure cases
7. Maintain minimum 70% coverage
8. Run tests before committing
