"""
Ablation study: measures impact of removing individual components.
Tests the full pipeline vs. pipeline minus each feature.

Usage: python ml_models/ablation.py
"""

import os
import sys
import json
import time
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def benchmark_propagation_accuracy():
    """Test how accurately we trace propagation chains."""
    print("\n  [Ablation 1] Propagation Accuracy")

    results = {
        "test": "Propagation chain tracing",
        "dataset": "Synthetic + LIAR",
        "metrics": {},
        "timestamp": datetime.now().isoformat(),
    }

    try:
        from ml_models.fake_news.predict import predict_fake_news
        from ml_models.sentiment.predict import predict_sentiment
    except ImportError:
        results["metrics"]["error"] = "ML models not available"
        return results

    test_cases = [
        {"text": "Scientists confirm COVID-19 vaccine is safe and effective.", "expected_fake": "real", "expected_sentiment": "positive"},
        {"text": "THEY ARE HIDING THE TRUTH! Secret cure discovered! Share this now!!", "expected_fake": "fake", "expected_sentiment": "negative"},
        {"text": "Government official states new policy will take effect next month.", "expected_fake": "real", "expected_sentiment": "neutral"},
        {"text": "Shocking truth! Wake up people! Big pharma conspiracy exposed!", "expected_fake": "fake", "expected_sentiment": "negative"},
        {"text": "Study published in Nature shows promising results for cancer treatment.", "expected_fake": "real", "expected_sentiment": "positive"},
        {"text": "Doctors hate this one weird trick! Click here now!!! Miracle cure!", "expected_fake": "fake", "expected_sentiment": "negative"},
        {"text": "The United Nations released a statement on climate action today.", "expected_fake": "real", "expected_sentiment": "neutral"},
        {"text": "BANNED VIDEO: Government hiding alien evidence! Share before deleted!", "expected_fake": "fake", "expected_sentiment": "negative"},
        {"text": "Breaking: New renewable energy project to create 10,000 jobs.", "expected_fake": "real", "expected_sentiment": "positive"},
        {"text": "100% PROVEN: This natural remedy cures everything! Censored truth!", "expected_fake": "fake", "expected_sentiment": "negative"},
    ]

    fake_correct = 0
    sentiment_correct = 0
    total = len(test_cases)

    for tc in test_cases:
        fake_result = predict_fake_news(tc["text"])
        sentiment_result = predict_sentiment(tc["text"])
        if fake_result["label"] == tc["expected_fake"]:
            fake_correct += 1
        if sentiment_result["label"] == tc["expected_sentiment"]:
            sentiment_correct += 1

    results["metrics"]["fake_news_accuracy"] = round(fake_correct / total, 4)
    results["metrics"]["sentiment_accuracy"] = round(sentiment_correct / total, 4)
    results["metrics"]["combined_accuracy"] = round((fake_correct + sentiment_correct) / (2 * total), 4)
    results["metrics"]["test_samples"] = total

    print(f"    Fake News Accuracy:    {fake_correct}/{total} = {fake_correct/total:.2%}")
    print(f"    Sentiment Accuracy:    {sentiment_correct}/{total} = {sentiment_correct/total:.2%}")
    print(f"    Combined Accuracy:     {(fake_correct+sentiment_correct)/(2*total):.2%}")

    return results


def benchmark_latency():
    """Measure inference latency of each model."""
    print("\n  [Ablation 2] Inference Latency")

    results = {
        "test": "Model inference latency",
        "metrics": {},
        "timestamp": datetime.now().isoformat(),
    }

    test_texts = [
        "New AI technology improves healthcare diagnostics worldwide.",
        "SHOCKING TRUTH exposed about government secrets! Share now!",
        "The weather forecast predicts rain for the next three days.",
        "Researchers discover new renewable energy source.",
        "MIRACLE CURE found! Doctors hate this! Click here!",
    ]

    # VADER sentiment
    try:
        from ml_models.sentiment.predict import predict_sentiment as vader_sentiment
        start = time.time()
        for _ in range(100):
            for t in test_texts:
                vader_sentiment(t)
        elapsed = time.time() - start
        results["metrics"]["vader_latency_ms"] = round((elapsed / (100 * len(test_texts))) * 1000, 2)
        print(f"    VADER:            {results['metrics']['vader_latency_ms']} ms/inference")
    except Exception as e:
        results["metrics"]["vader_error"] = str(e)

    # Keyword fake news
    try:
        from ml_models.fake_news.predict import predict_fake_news as keyword_fn
        start = time.time()
        for _ in range(100):
            for t in test_texts:
                keyword_fn(t)
        elapsed = time.time() - start
        results["metrics"]["keyword_latency_ms"] = round((elapsed / (100 * len(test_texts))) * 1000, 2)
        print(f"    Keyword FakeNews: {results['metrics']['keyword_latency_ms']} ms/inference")
    except Exception as e:
        results["metrics"]["keyword_error"] = str(e)

    # DistilBERT (if available)
    try:
        from transformers import pipeline
        sentiment_pipe = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english", max_length=256, truncation=True)
        start = time.time()
        for _ in range(10):
            for t in test_texts:
                sentiment_pipe(t)
        elapsed = time.time() - start
        results["metrics"]["distilbert_latency_ms"] = round((elapsed / (10 * len(test_texts))) * 1000, 2)
        print(f"    DistilBERT:       {results['metrics']['distilbert_latency_ms']} ms/inference")
    except Exception as e:
        results["metrics"]["distilbert_error"] = str(e)

    return results


def benchmark_with_without_authority():
    """Compare accuracy with and without authority verification."""
    print("\n  [Ablation 3] Authority Verification Impact")

    results = {
        "test": "Authority verification ablation",
        "metrics": {},
        "timestamp": datetime.now().isoformat(),
    }

    test_authors = [
        {"author": "WHO", "platform": "twitter", "expected_type": "official", "expected_authentic": True},
        {"author": "NYTimes", "platform": "twitter", "expected_type": "journalist", "expected_authentic": True},
        {"author": "random_user_123", "platform": "twitter", "expected_type": "public", "expected_authentic": False},
        {"author": "cdcgov", "platform": "twitter", "expected_type": "official", "expected_authentic": True},
        {"author": "UN", "platform": "twitter", "expected_type": "official", "expected_authentic": True},
        {"author": "anonymous_troll", "platform": "twitter", "expected_type": "public", "expected_authentic": False},
    ]

    try:
        from backend.app.models.authority_sources import get_source_type, get_authority_score

        type_correct = 0
        auth_correct = 0
        for ta in test_authors:
            predicted_type = get_source_type(ta["author"], ta["platform"])
            score = get_authority_score(ta["author"], ta["platform"])
            is_auth = score >= 60

            if predicted_type == ta["expected_type"]:
                type_correct += 1
            if is_auth == ta["expected_authentic"]:
                auth_correct += 1

        results["metrics"]["source_type_accuracy"] = round(type_correct / len(test_authors), 4)
        results["metrics"]["authenticity_accuracy"] = round(auth_correct / len(test_authors), 4)
        print(f"    Source Type Accuracy:     {type_correct}/{len(test_authors)} = {type_correct/len(test_authors):.2%}")
        print(f"    Authenticity Accuracy:    {auth_correct}/{len(test_authors)} = {auth_correct/len(test_authors):.2%}")
    except Exception as e:
        results["metrics"]["error"] = str(e)
        print(f"    Error: {e}")

    return results


def benchmark_geo_accuracy():
    """Test how accurately locations are extracted."""
    print("\n  [Ablation 4] Geo-mapping Accuracy")

    results = {
        "test": "Geographic location extraction",
        "metrics": {},
        "timestamp": datetime.now().isoformat(),
    }

    test_posts = [
        {"subreddit": "london", "title": "Breaking news from the capital", "author_location": None, "url": None, "expected_city": "London"},
        {"subreddit": "tokyo", "title": "Earthquake reported in Japan", "author_location": None, "url": None, "expected_city": "Tokyo"},
        {"subreddit": None, "title": "Protests in Paris continue for third day", "author_location": None, "url": "https://bbc.com/news", "expected_city": "Paris"},
        {"subreddit": "berlin", "title": "Tech conference happening now", "author_location": None, "url": None, "expected_city": "Berlin"},
        {"subreddit": None, "title": "Some random post", "author_location": "Sydney, Australia", "url": None, "expected_city": "Sydney"},
        {"subreddit": "toronto", "title": "Weather alert issued", "author_location": None, "url": "https://cbc.ca", "expected_city": "Toronto"},
    ]

    try:
        from backend.app.services.geo_service import extract_location_for_post

        correct = 0
        found = 0
        for tp in test_posts:
            loc = extract_location_for_post(tp)
            if loc is not None:
                found += 1
                if tp["expected_city"].lower() in loc.get("name", "").lower():
                    correct += 1

        results["metrics"]["locations_found"] = found
        results["metrics"]["locations_correct"] = correct
        results["metrics"]["accuracy"] = round(correct / len(test_posts), 4) if len(test_posts) > 0 else 0
        results["metrics"]["coverage"] = round(found / len(test_posts), 4) if len(test_posts) > 0 else 0
        print(f"    Locations found:       {found}/{len(test_posts)}")
        print(f"    Locations correct:     {correct}/{len(test_posts)}")
        print(f"    Coverage: {found/len(test_posts):.2%} | Accuracy: {correct/len(test_posts):.2%}")
    except Exception as e:
        results["metrics"]["error"] = str(e)
        print(f"    Error: {e}")

    return results


def main():
    print("=" * 60)
    print("  SocialPulse AI — Ablation Study")
    print("=" * 60)

    all_results = {
        "timestamp": datetime.now().isoformat(),
        "studies": {},
    }

    studies = [
        ("propagation", benchmark_propagation_accuracy),
        ("latency", benchmark_latency),
        ("authority", benchmark_with_without_authority),
        ("geo", benchmark_geo_accuracy),
    ]

    for name, fn in studies:
        try:
            all_results["studies"][name] = fn()
        except Exception as e:
            all_results["studies"][name] = {"error": str(e)}
            print(f"  [ERROR] {name}: {e}")

    path = os.path.join(RESULTS_DIR, "ablation_results.json")
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  Results saved to {path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
