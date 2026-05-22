import tweepy
from app.config import TWITTER_BEARER_TOKEN


client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN
)


# -----------------------------
# EXTRACT TWEET ID
# -----------------------------
def extract_tweet_id(url):
    return url.split("/status/")[-1].split("?")[0]

# -----------------------------
# FETCH TWEET DATA
# -----------------------------
def fetch_tweet(tweet_url):
    try:
        tweet_id = extract_tweet_id(tweet_url)

        # Call Twitter API
        response = client.get_tweet(
            id=tweet_id,
            tweet_fields=[
                "lang",
                "public_metrics",
                "created_at",
                "author_id",
                "text"
            ]
        )

        # -------------------------
        # FIX 1: handle missing data
        # -------------------------
        if not response or not response.data:
            print("DEBUG: Tweet not found or API returned empty response")
            return None

        tweet = response.data
        metrics = getattr(tweet, "public_metrics", {})

        # -------------------------
        # FIX 2: safe metric access
        # -------------------------
        return {
            "text": getattr(tweet, "text", ""),
            "language": getattr(tweet, "lang", "unknown"),
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0),
            "replies": metrics.get("reply_count", 0),
            "quotes": metrics.get("quote_count", 0)
        }

    except Exception as e:
        print("Twitter API Error:", str(e))
        return None