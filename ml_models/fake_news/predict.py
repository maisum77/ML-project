from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Optional
import os

MODEL_NAME = "roberta-base"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_model")

_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        try:
            _classifier = pipeline(
                "text-classification",
                model=MODEL_PATH,
                tokenizer=MODEL_PATH,
                max_length=512,
                truncation=True,
            )
        except Exception:
            _classifier = pipeline(
                "text-classification",
                model=MODEL_NAME,
                tokenizer=MODEL_NAME,
                max_length=512,
                truncation=True,
            )
    return _classifier


def predict_fake_news(text: str) -> dict:
    classifier = get_classifier()
    result = classifier(text)[0]
    label = result["label"]
    confidence = result["score"]

    if "NEGATIVE" in label or "FAKE" in label.upper():
        classification = "fake"
    else:
        classification = "real"

    return {
        "label": classification,
        "confidence": round(confidence * 100, 2),
    }
