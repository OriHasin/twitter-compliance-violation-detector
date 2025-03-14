from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db, AsyncSessionLocal
import datetime
import asyncio
from app.core.models import Violation, ScannedUser
from sqlalchemy import select, and_
from pydantic import BaseModel
from ..services.tweets_processor import process_user_tweets
from .policy_routes import load_policy_rules



# Create tweet router
tweet_router = APIRouter(prefix="/tweets", tags=["Tweets"])



class ProcessTweetsInput(BaseModel):
    usernames: List[str]
    policy_name: str




# Helper function to create a fresh DB session per username for background tasks
async def process_tweets_background(username: str, policy_rules: List[str]):
    """Process tweets using a dedicated database session per task."""
    print(f"🚀 STARTING BACKGROUND TASK for {username}")
    async with AsyncSessionLocal() as session:
        try:
            print(f"⏳ Processing tweets for {username}")
            await process_user_tweets(username, policy_rules, session)
            print(f"✅ Completed processing tweets for {username}")
        except Exception as e:
            print(f"❌ Error processing tweets for user: {username}. Error: {e}")






async def process_tweets_concurrently(usernames: List[str], policy_rules: List[str]):
    """Process multiple usernames concurrently."""
    
    # Create tasks for all usernames to process concurrently
    tasks = []
    for username in usernames:
        tasks.append(process_tweets_background(username, policy_rules))
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)





@tweet_router.post("/process", status_code=202)
async def process_tweets(input_data: ProcessTweetsInput, background_tasks: BackgroundTasks):
    """Process tweets from one or more Twitter usernames."""
    try:
        # Load policy rules
        policy_rules = await load_policy_rules(input_data.policy_name)
        print(f'✅ Loaded policy rules for {input_data.policy_name}')

        # Add a single background task that processes all usernames concurrently
        background_tasks.add_task(
            process_tweets_concurrently, 
            input_data.usernames, 
            policy_rules
        )
        
        # Prepare appropriate message based on number of usernames
        count = len(input_data.usernames)
        if count == 1:
            message = f"Processing tweets for username: {input_data.usernames[0]}"
        else:
            message = f"Processing tweets for {count} usernames"
        
        return {
            "message": message, 
            "usernames": input_data.usernames,
            "policy": input_data.policy_name,
            "status": "started"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting tweet processing: {str(e)}")




@tweet_router.get("/violations")
async def get_violations(
    start_date: Optional[datetime.datetime] = Query(None),
    end_date: Optional[datetime.datetime] = Query(None),
    username: Optional[str] = Query(None),
    policy: Optional[str] = Query(None),
    rule_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get stored violations with optional filtering.
    
    - start_date: Filter violations posted on or after this date
    - end_date: Filter violations posted on or before this date
    - policy: Filter by policy name
    - rule_id: Filter by specific rule ID
    - limit: Maximum number of violations to return (1-1000)
    - offset: Number of violations to skip
    """
    # Build query with filters
    conditions = []
    
    if start_date:
        conditions.append(Violation.posted_at >= start_date)
        print(start_date)
    
    if end_date:
        conditions.append(Violation.posted_at <= end_date)
    
    if policy:
        conditions.append(Violation.policy == policy)
    
    if rule_id:
        conditions.append(Violation.rule_id == rule_id)
    
    if username:
        conditions.append(Violation.username == username)
    
    # Apply filters if any
    if conditions:
        query = select(Violation).where(and_(*conditions)).limit(limit).offset(offset)
    else:
        query = select(Violation).limit(limit).offset(offset)
    
    result = await db.execute(query)
    violations = result.scalars().all()
    
    # Convert to list of dicts for JSON response
    violation_list = [
        {
            "id": v.id,
            "username": v.username,
            "tweet": v.tweet,
            "policy": v.policy,
            "rule_id": v.rule_id,
            "rule_violated": v.rule_violated,
            "reason": v.reason,
            "posted_at": v.posted_at
        }
        for v in violations
    ]
    
    return violation_list





@tweet_router.get("/scanned-users")
async def get_scanned_users(db: AsyncSession = Depends(get_db)):
    """Get list of scanned users and their last scan time."""
    
    query = select(ScannedUser)
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Note: Using last_scan field based on the model definition
    return [{"username": user.username, "last_scanned_at": user.last_scanned_at} for user in users]