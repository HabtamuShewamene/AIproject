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


def test_is_valid_tweet_url():
    assert twitter_client.is_valid_tweet_url("https://twitter.com/jack/status/20") is True
    assert twitter_client.is_valid_tweet_url("https://x.com/user_123/status/9876543210") is True
    assert twitter_client.is_valid_tweet_url("http://x.com/user/status/123?s=20") is True
    assert twitter_client.is_valid_tweet_url("https://facebook.com/post/123") is False
    assert twitter_client.is_valid_tweet_url("not a url") is False
    assert twitter_client.is_valid_tweet_url("") is False


def test_fetch_tweet_safe_with_invalid_url():
    result = twitter_client.fetch_tweet_safe("https://instagram.com/p/123")

    assert result["status"] == "invalid_url"
    assert "Twitter/X tweet link" in result["error"]
    assert result["data"] is None


def test_fetch_tweet_safe_with_missing_credentials(monkeypatch):
    monkeypatch.setattr(twitter_client, "APIFY_TOKEN", "")

    result = twitter_client.fetch_tweet_safe("https://x.com/user/status/123456789")

    assert result["status"] == "missing_credentials"
    assert "APIFY_TOKEN" in result["error"]
    assert result["data"] is None


def test_fetch_tweet_safe_success(monkeypatch):
    monkeypatch.setattr(twitter_client, "APIFY_TOKEN", "valid-test-token")
    mock_tweet = {"text": "Safe fetch tweet", "language": "en", "likes": 10, "retweets": 5, "replies": 1, "quotes": 0}
    monkeypatch.setattr(twitter_client, "fetch_tweet", lambda _url: mock_tweet)

    result = twitter_client.fetch_tweet_safe("https://x.com/user/status/123456789")

    assert result["status"] == "ok"
    assert result["error"] is None
    assert result["data"] == mock_tweet

