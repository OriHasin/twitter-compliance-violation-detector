# Simple Test Suite for Twitter Compliance Detector

This directory contains tests for the Twitter Compliance Violation Detector.

## Test Files

- `conftest.py` - Test fixtures and setup
- `test_api.py` - API endpoint tests
- `test_services.py` - Backend service tests
- `test_models.py` - Database model tests

## Setup and Running Tests

1. Install required packages (already available in the requirements.txt):


2. Run all tests:

```bash
python -m pytest
```

3. Run with coverage:

```bash
python -m pytest --cov
```