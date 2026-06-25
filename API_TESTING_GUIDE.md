# JSONPlaceholder API Testing Guide

This document explains how to test the JSONPlaceholder API endpoint (`https://jsonplaceholder.typicode.com/posts`) in this project.

## Quick Start

### 1. Run Simple API Tests (No Dependencies)
```bash
python test_api.py
```
This script runs all basic CRUD operations without requiring pytest. Great for quick validation.

### 2. Run Pytest Tests
```bash
pip install -r requirements.txt
pytest tests/test_jsonplaceholder_api.py -v
```

### 3. Run Tests via Shell Script
```bash
chmod +x run_tests.sh
./run_tests.sh [simple|pytest|all|coverage]
```

Examples:
```bash
./run_tests.sh simple      # Run simple script only
./run_tests.sh pytest      # Run pytest only
./run_tests.sh all         # Run both (default)
./run_tests.sh coverage    # Run with coverage report
```

## Test Files Overview

### `test_api.py` (Simple, standalone)
- ✅ No pytest required
- ✅ Human-readable output with emojis
- ✅ Comprehensive GET, POST, PUT, PATCH, DELETE tests
- ✅ Includes comments filtering and user-based filtering
- Usage: `python test_api.py`

### `tests/test_jsonplaceholder_api.py` (Pytest framework)
- ✅ Structured pytest class-based tests
- ✅ Parametrized tests for multiple scenarios
- ✅ Mocked tests for CI/CD without network
- ✅ Response time validation
- ✅ Coverage reporting support
- Usage: `pytest tests/test_jsonplaceholder_api.py -v`

## GitHub Actions Workflow

The `.github/workflows/test-api.yml` runs:
- **On push** to main/develop branches
- **On pull requests** to main
- **Scheduled daily** at 9 AM UTC
- **Matrix testing** across Python 3.9, 3.10, 3.11

Runs:
1. Simple API tests (`test_api.py`)
2. Pytest suite (`tests/test_jsonplaceholder_api.py`)
3. Coverage reports → uploaded to Codecov

## Test Coverage

### GET Endpoints
- ✅ GET /posts — retrieve all posts
- ✅ GET /posts/{id} — retrieve single post
- ✅ GET /posts/{id}/comments — get post comments
- ✅ GET /posts?userId={id} — filter by user

### POST / CREATE
- ✅ POST /posts — create new post
- ✅ Response includes auto-generated ID

### PUT / UPDATE
- ✅ PUT /posts/{id} — full update

### PATCH / PARTIAL UPDATE
- ✅ PATCH /posts/{id} — partial update

### DELETE
- ✅ DELETE /posts/{id} — delete post

### Performance & Resilience
- ✅ Response time validation (< 5s)
- ✅ Status code assertions
- ✅ Response structure validation

## Adding New Tests

### Add to `test_api.py` (Simple)
```python
def test_new_feature():
    """Test description"""
    print("\n🔍 Testing: GET /new-endpoint")
    response = requests.get(f"{BASE_URL}/new-endpoint")
    assert response.status_code == 200
    print(f"✅ Test passed")
```

### Add to `tests/test_jsonplaceholder_api.py` (Pytest)
```python
def test_new_feature(self):
    """Test description"""
    response = requests.get(f"{BASE_URL}/new-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert 'expected_field' in data
```

## Mocking for CI/CD (No Network)

Use the `@patch` decorator in pytest tests to mock network calls:
```python
@patch('requests.get')
def test_with_mock(self, mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "title": "Test"}]
    mock_get.return_value = mock_response
    
    # Your test logic here
```

See `tests/test_jsonplaceholder_api.py` for example.

## Troubleshooting

**Issue: `ImportError: No module named 'pytest'`**
```bash
pip install pytest pytest-cov pytest-mock
```

**Issue: Network timeout**
- JSONPlaceholder is very reliable, but if it times out:
  - Check your internet connection
  - Retry with `pytest tests/ --tb=short -v`
  - Use mocked tests if testing offline

**Issue: Tests hang**
- Ensure `requests` has reasonable timeouts
- Check `test_response_time()` for timeout validation

## Integration with Your Project

These tests are **separate from your chatbot/RAG system** (`app.py`, `build_index.py`). They validate external API behavior, useful for:
- Testing new data sources or APIs
- CI/CD validation before deploying
- Performance monitoring
- Documentation of expected API behavior

To integrate test results into your main app:
1. Use `test_api.py` as a health-check endpoint
2. Cache API responses in your retriever (see RAG patterns in `.github/copilot-instructions.md`)
3. Add fallback handling if API is down
