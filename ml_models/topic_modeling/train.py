from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_model")


def train_topic_model(texts: list, min_topic_size: int = 10):
    vectorizer = CountVectorizer(stop_words="english")

    model = BERTopic(
        language="english",
        top_n_words=10,
        min_topic_size=min_topic_size,
        verbose=True,
    )

    topics, probs = model.fit_transform(texts)

    model.save(MODEL_PATH, serialization="pickle")
    print(f"Topic model trained and saved to {MODEL_PATH}")

    topic_info = model.get_topic_info()
    print(f"Discovered {len(topic_info)} topics")

    return model, topics, probs
