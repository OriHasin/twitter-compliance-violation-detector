import asyncio
from tweets_fetcher import fetch_all_tweets
from openai_predictor import check_tweet_compliance
from models import Violation
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db




async def process_user_tweets(username: str, policy_rules: list, session: AsyncSession):
    tweets = await fetch_all_tweets(username, session)


    async def process_single_tweet(tweet_data):
        compliance_result = await check_tweet_compliance(tweet_data["text"], policy_rules)

        if compliance_result["violation"] == "YES":
            violation = Violation(
                tweet=tweet_data["text"],
                policy=compliance_result["policy"],
                rule_id=compliance_result["rule_id"], 
                rule_violated=compliance_result["rule_violated"],
                reason=compliance_result["reason"],
                posted_at=tweet_data["created_at"]
            )
            session.add(violation)
            await session.commit()


    # Create tasks for each tweet - placing them in ready queue asyncio
    tasks = [asyncio.create_task(process_single_tweet(tweet)) for tweet in tweets]


    # Wait for all tasks to complete (concurrent execution)
    await asyncio.gather(*tasks)
