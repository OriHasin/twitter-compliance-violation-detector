import tweepy
import datetime
from models import ScannedUser
from config import TWITTER_BEARER_TOKEN
from sqlalchemy.ext.asyncio import AsyncSession


# Twitter API Authentication
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)


async def get_last_scanned_date(username: str, db: AsyncSession):
    """Retrieve the last scanned date for a user from the database."""
    user = await db.get(ScannedUser, username)
    return user.last_scanned_at if user else None





async def save_last_scanned_date(username: str, db: AsyncSession):
    """Update the last scanned date for a user in the database."""
    user = await db.get(ScannedUser, username)
    if user:
        user.last_scanned_at = datetime.datetime.now(datetime.UTC)
    else:
        user = ScannedUser(username=username, last_scanned_at=datetime.datetime.now(datetime.UTC))
        db.add(user)
    await db.commit()





async def fetch_all_tweets(username: str, db: AsyncSession):
    # Get last scanned date for this user
    last_scanned = await get_last_scanned_date(username, db)
    
    query = f"from:{username} -is:retweet"

    tweet_list = []
    next_token = None
        
    kwargs = {
        "query": query,
        "max_results": 100,  # Fetch up to 100 tweets per request
        "tweet_fields": ["created_at", "text"],
        "next_token": next_token
    }
    if last_scanned:
        kwargs["start_time"] = last_scanned


    # Fetch tweets with pagination
    while True:
        
        tweets = await client.search_recent_tweets(**kwargs)

        if tweets.data:
            tweet_list.extend([{"text": tweet.text, "created_at": tweet.created_at} for tweet in tweets.data])

        # Check if there is a next token for pagination
        next_token = tweets.meta.get('next_token')
        if not next_token:
            break  # No more tweets to fetch
        kwargs["next_token"] = next_token

    # Update the last scanned date after successfully fetching tweets
    await save_last_scanned_date(username, db)
    
    return tweet_list
