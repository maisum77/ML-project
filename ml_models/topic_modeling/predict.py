from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import os
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_model")

_topic_model = None


def get_topic_model():
    global _topic_model
    if _topic_model is None:
        if os.path.exists(MODEL_PATH):
            _topic_model = BERTopic.load(MODEL_PATH)
        else:
            vectorizer = CountVectorizer(stop_words="english")
            _topic_model = BERTopic(
                language="english",
                top_n_words=10,
                verbose=False,
            )
    return _topic_model


def predict_topics(texts: list, min_topic_size: int = 10):
    model = get_topic_model()

    if not model.is_fitted:
        topics, probs = model.fit_transform(texts)
    else:
        topics, probs = model.transform(texts)

    topic_info = model.get_topic_info()

    results = []
    for i, (text, topic) in enumerate(zip(texts, topics)):
        if topic != -1:
            topic_words = model.get_topic(topic)
            keywords = [word for word, _ in topic_words[:5]]
        else:
            keywords = []

        results.append({
            "text": text[:200],
            "topic": topic,
            "keywords": keywords,
        })

    return results


def get_trending_topics(texts: list, top_n: int = 10):
    model = get_topic_model()

    if not model.is_fitted:
        model.fit(texts)

    topic_info = model.get_topic_info()
    trending = []

    for _, row in topic_info.head(top_n).iterrows():
        topic_id = row["Topic"]
        if topic_id == -1:
            continue
        topic_words = model.get_topic(topic_id)
        trending.append({
            "topic_id": topic_id,
            "name": row.get("Name", f"Topic {topic_id}"),
            "size": row.get("Count", 0),
            "keywords": [word for word, _ in topic_words[:5]],
        })

    return trending


def save_model():
    model = get_topic_model()
    if model.is_fitted:
        model.save(MODEL_PATH, serialization="pickle")
        print(f"Topic model saved to {MODEL_PATH}")
