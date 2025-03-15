import asyncio
from app.services.tweets_fetcher import fetch_all_tweets
from app.services.openai_predictor import check_tweet_compliance
from app.core.models import Violation
from sqlalchemy.ext.asyncio import AsyncSession




async def process_user_tweets(username: str, policy_rules: list, session: AsyncSession):
    user_violate_tweets = []
    tweets = await fetch_all_tweets(username, session)
    print(f'✅ Fetched {len(tweets)} tweets for {username}')

    async def process_single_tweet(tweet_data):
        try:
            compliance_result = await check_tweet_compliance(tweet_data["text"], policy_rules)
            if compliance_result.get("violation") == "YES":
                violation = Violation(
                    username=username,
                    tweet=compliance_result.get("tweet", ""),
                    policy=compliance_result.get("policy", ""),
                    rule_id=compliance_result.get("rule_id", ""),
                    rule_violated=compliance_result.get("rule_violated", ""),
                    reason=compliance_result.get("reason", ""),
                    posted_at=tweet_data.get("created_at", "")
                )
                user_violate_tweets.append(violation)
                print(f'🚨 Violation found for tweet: {tweet_data["text"]}, by user: {username}')

        except Exception as e:
            print(f'❌ Error processing a specific tweet from {username}, Error: {str(e)}')


    tasks = [asyncio.create_task(process_single_tweet(tweet)) for tweet in tweets]
    # Wait for all tasks to complete (concurrent execution)
    await asyncio.gather(*tasks)

    
    # commit the violations to the database
    if user_violate_tweets:
        print(f'🔍 Found {len(user_violate_tweets)} violations for {username}')
        session.add_all(user_violate_tweets)
        await session.commit()
        print(f'✅ Committed {len(user_violate_tweets)} violations for {username} to the database')
    else:
        print(f'🎉 No violations found for {username}')
