"""
Train the sentiment analysis model using DistilBERT on the SST-2 dataset.
Run: python -m ml_models.sentiment.train
"""

import os
import time
import json
import numpy as np
from datetime import datetime
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from datasets import load_dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "results")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_model")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def train(epochs=3, batch_size=16, learning_rate=2e-5):
    print("=" * 60)
    print("  Training Sentiment Classifier — DistilBERT on SST-2")
    print("=" * 60)

    id2label = {0: "negative", 1: "positive"}
    label2id = {"negative": 0, "positive": 1}

    print("[1/5] Loading SST-2 dataset...")
    dataset = load_dataset("glue", "sst2")
    print(f"  Train: {len(dataset['train'])} | Validation: {len(dataset['validation'])}")
    test_split = dataset["validation"].train_test_split(test_size=0.5, seed=42)

    print("[2/5] Loading DistilBERT tokenizer & model...")
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2, id2label=id2label, label2id=label2id
    )

    def tokenize_fn(examples):
        return tokenizer(examples["sentence"], truncation=True, max_length=256)

    tokenized_train = dataset["train"].map(tokenize_fn, batched=True)
    tokenized_val = test_split["train"].map(tokenize_fn, batched=True)
    tokenized_test = test_split["test"].map(tokenize_fn, batched=True)

    print("[3/5] Configuring training...")
    training_args = TrainingArguments(
        output_dir=MODEL_DIR,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
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

    print("[4/5] Training...")
    start = time.time()
    trainer.train()
    elapsed = time.time() - start
    print(f"  Training completed in {elapsed:.1f}s")

    print("[5/5] Evaluating on test set...")
    test_results = trainer.evaluate(tokenized_test)
    print(f"  Accuracy:  {test_results['eval_accuracy']:.4f}")
    print(f"  Precision: {test_results['eval_precision']:.4f}")
    print(f"  Recall:    {test_results['eval_recall']:.4f}")
    print(f"  F1 Score:  {test_results['eval_f1']:.4f}")

    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print(f"  Model saved to {MODEL_DIR}")

    results = {
        "model": "DistilBERT-base",
        "dataset": "SST-2 (GLUE)",
        "timestamp": datetime.now().isoformat(),
        "training_time_sec": round(elapsed, 1),
        "epochs": epochs,
        "batch_size": batch_size,
        "test_accuracy": round(test_results["eval_accuracy"], 4),
        "test_precision": round(test_results["eval_precision"], 4),
        "test_recall": round(test_results["eval_recall"], 4),
        "test_f1": round(test_results["eval_f1"], 4),
    }

    result_path = os.path.join(RESULTS_DIR, "sentiment_results.json")
    with open(result_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to {result_path}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    args = parser.parse_args()
    train(epochs=args.epochs, batch_size=args.batch, learning_rate=args.lr)
