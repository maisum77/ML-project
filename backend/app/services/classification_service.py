from typing import Optional


async def classify_text(text: str, source: Optional[str] = None):
    from ml_models.sentiment.predict import predict_sentiment
    from ml_models.fake_news.predict import predict_fake_news

    sentiment_result = predict_sentiment(text)
    fake_result = predict_fake_news(text)

    return {
        "text": text,
        "classification": fake_result["label"],
        "confidence": fake_result["confidence"],
        "sentiment": sentiment_result["label"],
        "sentiment_score": sentiment_result["score"],
        "source": source,
    }
