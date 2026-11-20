import pytest
from src.enterprise_cleaner import clean_tweet_text, is_valid_tweet, normalise_for_dedup


def test_html_unescaping():
    raw = 'Watching &quot;Inception&quot; &amp; eating popcorn &lt;3'
    cleaned = clean_tweet_text(raw)
    assert cleaned == 'Watching "Inception" & eating popcorn <3'


def test_url_removal():
    raw = 'Check this out http://example.com/xyz and https://t.co/abc today'
    cleaned = clean_tweet_text(raw)
    assert cleaned == 'Check this out and today'


def test_mention_standardization():
    raw = '@elonmusk congrats on the launch @SpaceX!'
    cleaned = clean_tweet_text(raw)
    assert cleaned == '@user congrats on the launch @user!'


def test_hashtag_extraction():
    raw = 'This update is #awesome and #unbelievable'
    cleaned = clean_tweet_text(raw)
    assert cleaned == 'This update is awesome and unbelievable'


def test_elongation_compression():
    raw = 'I am sooooooo haaaapppyyyy!!'
    cleaned = clean_tweet_text(raw)
    assert cleaned == 'I am soo haappyy!'


def test_repeated_punctuation():
    raw = 'What is going on???? Really!!!!!!'
    cleaned = clean_tweet_text(raw)
    assert cleaned == 'What is going on? Really!'


def test_contractions_preserved():
    raw = "I can't believe it didn't work."
    cleaned = clean_tweet_text(raw)
    assert cleaned == "I can't believe it didn't work."


def test_is_valid_tweet():
    assert is_valid_tweet("Great job @user!") is True
    assert is_valid_tweet("@user") is False
    assert is_valid_tweet("@user @user") is False
    assert is_valid_tweet("   ") is False
    assert is_valid_tweet("...") is False
    assert is_valid_tweet(None) is False


def test_dedup_normalization():
    assert normalise_for_dedup("  Hello   WORLD!  ") == "hello world!"
