import tweepy
from tweepy.errors import TooManyRequests, TwitterServerError
import datetime
import json
from app.core.models import ScannedUser
from app.core.config import TWITTER_BEARER_TOKEN, USE_SAMPLE_DATA
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Twitter API Authentication
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)




async def get_last_scanned_date(username: str, db: AsyncSession):
    """Retrieve the last scanned date for a user from the database."""
    # Query by username since it's not the primary key
    result = await db.execute(select(ScannedUser).where(ScannedUser.username == username))
    user = result.scalars().first()
    return user.last_scanned_at if user else None




async def save_last_scanned_date(username: str, db: AsyncSession):
    """Update the last scanned date for a user in the database."""
    # Query by username
    result = await db.execute(select(ScannedUser).where(ScannedUser.username == username))
    user = result.scalars().first()
    
    # Create a timezone-naive datetime using modern approach
    current_time = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    
    if user:
        user.last_scanned_at = current_time
    else:
        user = ScannedUser(username=username, last_scanned_at=current_time)
        db.add(user)
    await db.commit()




async def fetch_sample_tweets(username: str, db: AsyncSession):
    """Fetch pre-generated sample tweets for testing without Twitter API."""
    sample_file_path = "./data/pre_generated_tweets.json"
    
    print(f"📄 Loading sample tweets from {sample_file_path}")
    with open(sample_file_path, "r") as f:
        data = json.load(f)
    

    
    # Convert created_at strings to datetime objects
    tweets = []
    for tweet in data["tweets"]:
        created_at = datetime.datetime.fromisoformat(tweet["created_at"].replace('Z', ''))
        tweets.append({
            "text": tweet["text"],
            "created_at": created_at
        })

    print(f"✅ Loaded {len(tweets)} sample tweets")
    # Update last scanned date for this user
    await save_last_scanned_date(username, db)
    return tweets




@retry(
      stop=stop_after_attempt(3),
      wait=wait_exponential(multiplier=1, min=2, max=30), 
      retry=retry_if_exception_type((
          ConnectionError, 
          TimeoutError,
          tweepy.errors.TwitterServerError
      ))
)
async def fetch_tweets_page_with_retry(**kwargs):
    return await client.search_recent_tweets(**kwargs)




async def fetch_all_tweets(username: str, db: AsyncSession):
    # Check if we should use sample data for testing
    if USE_SAMPLE_DATA:
        print(f"🔍 Using sample tweets data")
        return await fetch_sample_tweets(username, db)
    
    # Get last scanned date for this user
    last_scanned = await get_last_scanned_date(username, db)
    
    query = f"from:{username} -is:retweet"
    tweet_list = []
    next_token = None
        
    kwargs = {
        "query": query,
        "max_results": 100,  # Fetch up to 100 tweets per request
        "tweet_fields": ["created_at", "text"]
    }
    if last_scanned:
        kwargs["start_time"] = last_scanned


    print(f'🚀 Start fetching tweets for {username} from date: {last_scanned}')
    # Fetch tweets with pagination
    while True:
        try:
            print(f'🔍 Fetching tweets for {username} from date: {last_scanned}')
            tweets = await fetch_tweets_page_with_retry(**kwargs)
            print(f'🔍 Tweets response for {username}: {tweets}')
                
            if tweets.data:
                tweet_list.extend([
                    {
                        "text": tweet.text, 
                        "created_at": tweet.created_at
                    } 
                    for tweet in tweets.data
                ])

            # Check if there is a next token for pagination
            if not hasattr(tweets, 'meta') or not tweets.meta.get('next_token'):
                break  # No more tweets to fetch
                        
            next_token = tweets.meta.get('next_token')
            kwargs["next_token"] = next_token

        except TooManyRequests:
            if tweet_list:
                print(f"❌ Got Rate limit error, but fetched {len(tweet_list)} tweets from previous page")
                break
            raise


    # Update the last scanned date after successfully fetching tweets
    if tweet_list:
        print(f"✅ Successfully fetched {len(tweet_list)} tweets for {username}")
        await save_last_scanned_date(username, db)
    
    return tweet_list