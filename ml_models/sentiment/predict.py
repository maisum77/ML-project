from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Optional
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_model")
vader = SentimentIntensityAnalyzer()

_distilbert_classifier = None


def get_distilbert_classifier():
    global _distilbert_classifier
    if _distilbert_classifier is None:
        try:
            _distilbert_classifier = pipeline(
                "text-classification",
                model=MODEL_PATH,
                tokenizer=MODEL_PATH,
                max_length=512,
                truncation=True,
                return_all_scores=True,
            )
        except Exception:
            _distilbert_classifier = None
    return _distilbert_classifier


def predict_sentiment(text: str) -> dict:
    classifier = get_distilbert_classifier()

    if classifier:
        try:
            results = classifier(text)[0]
            label_map = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
            best = max(results, key=lambda x: x["score"])
            return {
                "label": label_map.get(best["label"], "neutral"),
                "score": round(best["score"] * 100, 2),
                "model": "distilbert",
            }
        except Exception:
            pass

    scores = vader.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "label": label,
        "score": round(abs(compound) * 100, 2),
        "model": "vader",
    }
