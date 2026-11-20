from app import twitter_client


def test_extract_tweet_id_handles_query_string():
    url = "https://twitter.com/example/status/1234567890?s=20"

    assert twitter_client.extract_tweet_id(url) == "1234567890"


def test_fetch_tweet_returns_metrics_with_safe_defaults(monkeypatch):
    monkeypatch.setattr(
        twitter_client,
        "_run_actor",
        lambda _run_input: [
            {
                "text": "A test tweet",
                "lang": "en",
                "likeCount": 5,
                "retweetCount": 2,
            }
        ],
    )

    result = twitter_client.fetch_tweet("https://twitter.com/example/status/123")

    assert result == {
        "text": "A test tweet",
        "language": "en",
        "likes": 5,
        "retweets": 2,
        "replies": 0,
        "quotes": 0,
    }


def test_fetch_tweet_returns_none_when_api_has_no_data(monkeypatch):
    monkeypatch.setattr(
        twitter_client,
        "_run_actor",
        lambda _run_input: [],
    )

    assert twitter_client.fetch_tweet("https://twitter.com/example/status/123") is None
