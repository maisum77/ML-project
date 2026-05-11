"""
End-to-end training pipeline for all three models:
  1. Fake News Classifier (RoBERTa on LIAR dataset)
  2. Sentiment Analysis (DistilBERT on SST-2)
  3. Topic Modeling (BERTopic on 20 Newsgroups)

Usage:
    python ml_models/train_all.py              # train all
    python ml_models/train_all.py --model fake_news   # train one
    python ml_models/train_all.py --model sentiment
    python ml_models/train_all.py --model topic
    python ml_models/train_all.py --epochs 5 --batch 16
"""

import argparse
import os
import sys
import time
import json
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

_training_log = {}


def log_metric(model_name, metric_name, value):
    if model_name not in _training_log:
        _training_log[model_name] = {}
    _training_log[model_name][metric_name] = value


def save_results():
    path = os.path.join(RESULTS_DIR, "training_results.json")
    _training_log["timestamp"] = datetime.now().isoformat()
    with open(path, "w") as f:
        json.dump(_training_log, f, indent=2, default=str)
    print(f"\n[Results] Saved to {path}")


def train_fake_news(epochs=3, batch_size=8):
    print("\n" + "=" * 60)
    print("  TRAINING: Fake News Classifier (RoBERTa on LIAR)")
    print("=" * 60)

    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        Trainer, TrainingArguments, DataCollatorWithPadding
    )
    from datasets import load_dataset
    import numpy as np
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support

    print("[1/5] Loading LIAR dataset...")
    dataset = load_dataset("liar", trust_remote_code=True)
    label_map = {
        "pants-fire": 0, "false": 0, "barely-true": 0,
        "half-true": 1, "mostly-true": 1, "true": 1,
    }
    id2label = {0: "fake", 1: "real"}
    label2id = {"fake": 0, "real": 1}

    def preprocess(examples):
        return {"labels": [label_map.get(l, 1) for l in examples["label"]]}

    dataset = dataset.map(preprocess, batched=True)

    print(f"  Train: {len(dataset['train'])} | Val: {len(dataset['validation'])} | Test: {len(dataset['test'])}")

    print("[2/5] Loading RoBERTa tokenizer & model...")
    model_name = "roberta-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=2, id2label=id2label, label2id=label2id
    )

    def tokenize_fn(examples):
        texts = [ex["statement"] if "statement" in ex else str(ex.get("text", "")) for ex in [
            {"statement": examples["statement"][i]} if "statement" in examples else {"text": ""}
            for i in range(len(examples.get("statement", examples.get("text", [""]))))
        ]]
        return tokenizer(examples.get("statement", examples.get("text", [""])), truncation=True, max_length=256)

    tokenized_train = dataset["train"].map(tokenize_fn, batched=True)
    tokenized_val = dataset["validation"].map(tokenize_fn, batched=True)
    tokenized_test = dataset["test"].map(tokenize_fn, batched=True)

    print("[3/5] Setting up training...")
    training_args = TrainingArguments(
        output_dir=os.path.join(os.path.dirname(__file__), "fake_news", "saved_model"),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir=os.path.join(RESULTS_DIR, "logs", "fake_news"),
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        report_to=[],
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=1)
        acc = accuracy_score(labels, preds)
        prec, rec, f1, _ = precision_recall_fscore_support(labels, preds, average="binary", zero_division=0)
        return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )

    print("[4/5] Training RoBERTa on LIAR...")
    start = time.time()
    trainer.train()
    training_time = time.time() - start

    print("[5/5] Evaluating on test set...")
    test_results = trainer.evaluate(tokenized_test)
    log_metric("fake_news_roberta", "test_accuracy", round(test_results["eval_accuracy"], 4))
    log_metric("fake_news_roberta", "test_precision", round(test_results["eval_precision"], 4))
    log_metric("fake_news_roberta", "test_recall", round(test_results["eval_recall"], 4))
    log_metric("fake_news_roberta", "test_f1", round(test_results["eval_f1"], 4))
    log_metric("fake_news_roberta", "training_time_sec", round(training_time, 1))
    log_metric("fake_news_roberta", "dataset", "LIAR")
    log_metric("fake_news_roberta", "train_samples", len(dataset["train"]))
    log_metric("fake_news_roberta", "test_samples", len(dataset["test"]))

    print(f"  Accuracy: {test_results['eval_accuracy']:.4f}")
    print(f"  Precision: {test_results['eval_precision']:.4f}")
    print(f"  Recall: {test_results['eval_recall']:.4f}")
    print(f"  F1 Score: {test_results['eval_f1']:.4f}")
    print(f"  Time: {training_time:.1f}s")


def train_sentiment(epochs=3, batch_size=16):
    print("\n" + "=" * 60)
    print("  TRAINING: Sentiment Analysis (DistilBERT on SST-2)")
    print("=" * 60)

    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        Trainer, TrainingArguments, DataCollatorWithPadding
    )
    from datasets import load_dataset
    import numpy as np
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support

    print("[1/5] Loading SST-2 dataset...")
    dataset = load_dataset("glue", "sst2")
    id2label = {0: "negative", 1: "positive"}
    label2id = {"negative": 0, "positive": 1}

    print(f"  Train: {len(dataset['train'])} | Val: {len(dataset['validation'])}")
    test_split = dataset["validation"].train_test_split(test_size=0.5, seed=42)

    print("[2/5] Loading DistilBERT tokenizer & model...")
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=2, id2label=id2label, label2id=label2id
    )

    def tokenize_fn(examples):
        return tokenizer(examples["sentence"], truncation=True, max_length=256)

    tokenized_train = dataset["train"].map(tokenize_fn, batched=True)
    tokenized_val = test_split["train"].map(tokenize_fn, batched=True)
    tokenized_test = test_split["test"].map(tokenize_fn, batched=True)

    print("[3/5] Setting up training...")
    training_args = TrainingArguments(
        output_dir=os.path.join(os.path.dirname(__file__), "sentiment", "saved_model"),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir=os.path.join(RESULTS_DIR, "logs", "sentiment"),
        logging_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        report_to=[],
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=1)
        acc = accuracy_score(labels, preds)
        prec, rec, f1, _ = precision_recall_fscore_support(labels, preds, average="binary", zero_division=0)
        return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )

    print("[4/5] Training DistilBERT on SST-2...")
    start = time.time()
    trainer.train()
    training_time = time.time() - start

    print("[5/5] Evaluating on test set...")
    test_results = trainer.evaluate(tokenized_test)
    log_metric("sentiment_distilbert", "test_accuracy", round(test_results["eval_accuracy"], 4))
    log_metric("sentiment_distilbert", "test_precision", round(test_results["eval_precision"], 4))
    log_metric("sentiment_distilbert", "test_recall", round(test_results["eval_recall"], 4))
    log_metric("sentiment_distilbert", "test_f1", round(test_results["eval_f1"], 4))
    log_metric("sentiment_distilbert", "training_time_sec", round(training_time, 1))
    log_metric("sentiment_distilbert", "dataset", "SST-2")
    log_metric("sentiment_distilbert", "train_samples", len(dataset["train"]))
    log_metric("sentiment_distilbert", "test_samples", len(tokenized_test))

    print(f"  Accuracy: {test_results['eval_accuracy']:.4f}")
    print(f"  Precision: {test_results['eval_precision']:.4f}")
    print(f"  Recall: {test_results['eval_recall']:.4f}")
    print(f"  F1 Score: {test_results['eval_f1']:.4f}")
    print(f"  Time: {training_time:.1f}s")


def train_topic_model(min_topic_size=10):
    print("\n" + "=" * 60)
    print("  TRAINING: Topic Modeling (BERTopic on 20 Newsgroups)")
    print("=" * 60)

    from sklearn.datasets import fetch_20newsgroups
    from sklearn.feature_extraction.text import CountVectorizer
    from bertopic import BERTopic
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

    print("[1/4] Loading 20 Newsgroups dataset...")
    newsgroups = fetch_20newsgroups(subset="all", remove=("headers", "footers", "quotes"))
    texts = [t for t in newsgroups.data if len(t.strip()) > 100][:5000]
    true_labels = newsgroups.target[:len(texts)]

    print(f"  Documents: {len(texts)} | Categories: {len(set(true_labels))}")

    print("[2/4] Training BERTopic model...")
    vectorizer = CountVectorizer(stop_words="english", max_features=2000)
    start = time.time()
    model = BERTopic(
        language="english",
        top_n_words=10,
        min_topic_size=min_topic_size,
        verbose=True,
    )
    topics, probs = model.fit_transform(texts)
    training_time = time.time() - start

    print("[3/4] Computing clustering metrics...")
    topic_info = model.get_topic_info()
    n_topics = len(topic_info[topic_info["Topic"] != -1])
    outlier_ratio = len([t for t in topics if t == -1]) / len(topics)

    from collections import Counter
    topic_counts = Counter(topics)
    top_5 = topic_counts.most_common(5)

    print("[4/4] Computing NMI score...")
    valid_idx = [i for i, t in enumerate(topics) if t != -1]
    if len(valid_idx) > 100:
        filtered_topics = [topics[i] for i in valid_idx]
        filtered_labels = [true_labels[i] for i in valid_idx]
        nmi = normalized_mutual_info_score(filtered_labels, filtered_topics)
    else:
        nmi = 0.0

    log_metric("topic_bertopic", "num_topics", n_topics)
    log_metric("topic_bertopic", "outlier_ratio", round(outlier_ratio, 4))
    log_metric("topic_bertopic", "nmi_score", round(nmi, 4))
    log_metric("topic_bertopic", "training_time_sec", round(training_time, 1))
    log_metric("topic_bertopic", "dataset", "20 Newsgroups")
    log_metric("topic_bertopic", "samples", len(texts))
    log_metric("topic_bertopic", "top_topics", [
        {"topic": t, "count": c, "words": model.get_topic(t)[:5] if t != -1 else []}
        for t, c in top_5
    ])

    print(f"  Topics found: {n_topics}")
    print(f"  Outlier ratio: {outlier_ratio:.4f}")
    print(f"  NMI Score: {nmi:.4f}")
    print(f"  Time: {training_time:.1f}s")

    model_path = os.path.join(os.path.dirname(__file__), "topic_modeling", "saved_model")
    model.save(model_path, serialization="pickle")
    print(f"  Model saved to {model_path}")


def main():
    parser = argparse.ArgumentParser(description="Train all ML models for SocialPulse AI")
    parser.add_argument("--model", choices=["all", "fake_news", "sentiment", "topic"], default="all")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--min_topic_size", type=int, default=10)
    args = parser.parse_args()

    print("=" * 60)
    print("  SocialPulse AI — ML Model Training Pipeline")
    print("=" * 60)

    try:
        if args.model in ("all", "topic"):
            train_topic_model(min_topic_size=args.min_topic_size)
    except Exception as e:
        print(f"[WARNING] Topic modeling failed: {e}")
        log_metric("topic_bertopic", "error", str(e))

    try:
        if args.model in ("all", "fake_news"):
            train_fake_news(epochs=args.epochs, batch_size=args.batch)
    except Exception as e:
        print(f"[WARNING] Fake news training failed: {e}")
        log_metric("fake_news_roberta", "error", str(e))

    try:
        if args.model in ("all", "sentiment"):
            train_sentiment(epochs=args.epochs, batch_size=args.batch)
    except Exception as e:
        print(f"[WARNING] Sentiment training failed: {e}")
        log_metric("sentiment_distilbert", "error", str(e))

    save_results()
    print("\n" + "=" * 60)
    print("  Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
