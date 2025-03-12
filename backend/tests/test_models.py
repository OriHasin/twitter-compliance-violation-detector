import pytest
import datetime
from app.core.models import Violation, ScannedUser

def test_violation_model():
    """Test basic Violation model attributes."""
    test_time = datetime.datetime.now()
    
    violation = Violation(
        tweet="Test tweet",
        policy="Test Policy",
        rule_id="TEST-001", 
        rule_violated="Test rule",
        reason="Test reason",
        posted_at=test_time
    )
    
    assert violation.tweet == "Test tweet"
    assert violation.policy == "Test Policy"
    assert violation.rule_id == "TEST-001"
    assert violation.posted_at == test_time

def test_scanned_user_model():
    """Test basic ScannedUser model attributes."""
    test_time = datetime.datetime.now()
    
    user = ScannedUser(
        username="test_user",
        last_scanned_at=test_time
    )
    
    assert user.username == "test_user"
    assert user.last_scanned_at == test_time