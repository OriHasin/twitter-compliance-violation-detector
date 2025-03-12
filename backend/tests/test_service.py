import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import datetime

@pytest.mark.asyncio
async def test_openai_predictor():
    """Test OpenAI predictor service."""
    from app.services.openai_predictor import check_tweet_compliance
    
    # Mock OpenAI API response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(
            content=json.dumps({
                "violation": "NO",
                "tweet": "Test tweet",
                "policy": "",
                "rule_id": "",
                "rule_violated": "",
                "reason": ""
            })
        ))
    ]
    
    # Create async mock for API call
    async def mock_create(*args, **kwargs):
        return mock_response
    
    # Patch the OpenAI client
    with patch("app.services.openai_predictor.client.chat.completions.create", 
               side_effect=mock_create):
        
        # Test the function
        result = await check_tweet_compliance("Test tweet", [])
        
        # Verify result
        assert result["violation"] == "NO"

@pytest.mark.asyncio
async def test_tweet_processor(db_session):
    """Test tweet processor with mocks."""
    from app.services.tweets_processor import process_user_tweets
    
    # Mock data
    tweets = [
        {"text": "Test tweet", "created_at": datetime.datetime.now()}
    ]
    policy_rules = [{"rule_id": "TEST-001", "description": "Test rule"}]
    
    # Create a mock violation result
    mock_compliance_result = {
        "violation": "YES",
        "tweet": "Test tweet",
        "policy": "Test Policy",
        "rule_id": "TEST-001",
        "rule_violated": "Test rule",
        "reason": "Test reason"
    }
    
    # Mock tweet fetching
    with patch("app.services.tweets_processor.fetch_all_tweets", 
               AsyncMock(return_value=tweets)):
        
        # Mock compliance checking - now returning a violation
        with patch("app.services.tweets_processor.check_tweet_compliance", 
                  AsyncMock(return_value=mock_compliance_result)):
            
            # Call the function
            await process_user_tweets("test_user", policy_rules, db_session)
            
            # With a violation, at least one of these should be called
            assert db_session.add.called or db_session.add_all.called