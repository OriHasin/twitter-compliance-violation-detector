import pytest
from unittest.mock import patch, MagicMock
import json
from io import BytesIO

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/system/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"

def test_list_policies(client):
    """Test listing available policies."""
    # Mock the route handler to avoid network issues
    with patch("app.routes.policy_routes.list_available_policies", 
              return_value={"policies": ["policy1", "policy2"]}):
        
        response = client.get("/policies/list")
        assert response.status_code == 200
        assert "policies" in response.json()

def test_process_tweets(client):
    """Test processing tweets."""
    # Data to send
    request_data = {
        "usernames": ["test_user"],
        "policy_name": "employee_social_media_policy"
    }
    
    # Mock the route handler to avoid network issues
    with patch("app.routes.policy_routes.load_policy_rules", 
              return_value=[{"rule_id": "TEST-001", "description": "Test rule"}]):
        with patch("app.routes.tweet_routes.process_user_tweets", 
                  return_value=None) as mock_process:
            
            response = client.post("/tweets/process", json=request_data)
            assert response.status_code == 202
            assert response.json() == {
                "message": "Processing tweets for username: test_user",
                "usernames": ["test_user"],
                "policy": "employee_social_media_policy",
                "status": "started"
            }