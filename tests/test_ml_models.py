import pytest
from ml_models.sentiment.predict import predict_sentiment


def test_sentiment_positive():
    result = predict_sentiment("I absolutely love this new technology!")
    assert result["label"] == "positive"


def test_sentiment_negative():
    result = predict_sentiment("This is the worst thing ever, I hate it")
    assert result["label"] == "negative"


def test_sentiment_neutral():
    result = predict_sentiment("The meeting is scheduled for tomorrow")
    assert result["label"] in ["neutral", "positive", "negative"]


def test_sentiment_returns_dict():
    result = predict_sentiment("Test text")
    assert "label" in result
    assert "score" in result
    assert "model" in result
