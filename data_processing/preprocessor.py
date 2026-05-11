import re
import spacy
from langdetect import detect, LangDetectException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Optional

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

vader = SentimentIntensityAnalyzer()


class TextPreprocessor:
    def __init__(self):
        self.stopwords = set(nlp.Defaults.stop_words)

    def clean_text(self, text: str) -> str:
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'#(\w+)', r'\1', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def detect_language(self, text: str) -> str:
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"

    def tokenize(self, text: str) -> list:
        doc = nlp(text.lower())
        tokens = [
            token.lemma_ for token in doc
            if not token.is_stop and not token.is_punct and len(token.text) > 2
        ]
        return tokens

    def get_sentiment(self, text: str) -> dict:
        scores = vader.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        return {"label": label, "score": compound, "scores": scores}

    def preprocess(self, text: str) -> dict:
        cleaned = self.clean_text(text)
        language = self.detect_language(text)
        tokens = self.tokenize(cleaned)
        sentiment = self.get_sentiment(cleaned)

        return {
            "original": text,
            "cleaned": cleaned,
            "language": language,
            "tokens": tokens,
            "sentiment": sentiment,
        }
