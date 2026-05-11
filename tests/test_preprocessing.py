import pytest
from data_processing.preprocessor import TextPreprocessor

preprocessor = TextPreprocessor()


def test_clean_text():
    text = "Check this out! https://example.com #AI @user <b>bold</b>"
    cleaned = preprocessor.clean_text(text)
    assert "https://example.com" not in cleaned
    assert "<b>" not in cleaned
    assert "AI" in cleaned


def test_detect_language():
    assert preprocessor.detect_language("This is English text") == "en"
    assert preprocessor.detect_language("Este es texto en espanol") == "es"


def test_tokenize():
    tokens = preprocessor.tokenize("The quick brown fox jumps over the lazy dog")
    assert len(tokens) > 0
    assert "the" not in tokens


def test_sentiment_positive():
    result = preprocessor.get_sentiment("I love this amazing product!")
    assert result["label"] == "positive"


def test_sentiment_negative():
    result = preprocessor.get_sentiment("This is terrible and I hate it")
    assert result["label"] == "negative"


def test_sentiment_neutral():
    result = preprocessor.get_sentiment("The weather is okay today")
    assert result["label"] in ["neutral", "positive"]


def test_preprocess_pipeline():
    result = preprocessor.preprocess("Hello world! This is a test.")
    assert "cleaned" in result
    assert "tokens" in result
    assert "sentiment" in result
    assert result["language"] == "en"
