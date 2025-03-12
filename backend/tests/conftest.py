import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.core.database import get_db
from main import app

@pytest.fixture
def db_session():
    """Simple mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    
    # Configure execute result
    result = MagicMock()
    result.scalars = MagicMock()
    result.scalars().first = MagicMock(return_value=None)
    result.scalars().all = MagicMock(return_value=[])
    session.execute.return_value = result
    
    return session

@pytest.fixture
def client(db_session):
    """Create test client with mocked DB."""
    # Override the database dependency
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create TestClient
    test_client = TestClient(app)
    
    yield test_client
    
    # Clean up
    app.dependency_overrides = {}

@pytest.fixture
def sample_policy():
    """Sample policy for testing."""
    return {
        "policy_name": "Test Policy",
        "rules": [
            {
                "rule_id": "TEST-001",
                "category": "Test Category",
                "description": "Test rule description"
            }
        ]
    }

@pytest.fixture
def sample_violation():
    """Sample violation for testing."""
    from app.core.models import Violation
    import datetime
    
    return Violation(
        id=1,
        tweet="Test violation tweet",
        policy="Test Policy",
        rule_id="TEST-001",
        rule_violated="Test rule",
        reason="Test reason",
        posted_at=datetime.datetime.now()
    )