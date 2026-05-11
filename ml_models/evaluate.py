"""
Comprehensive evaluation script for all models.
Generates confusion matrices, ROC curves, classification reports,
model comparison tables, and saves everything to results/.

Usage:
    python ml_models/evaluate.py              # evaluate all
    python ml_models/evaluate.py --model fake_news
    python ml_models/evaluate.py --compare     # model comparison table only
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(os.path.join(RESULTS_DIR, "charts"), exist_ok=True)

_eval_results = {}


def save_eval():
    path = os.path.join(RESULTS_DIR, "evaluation_results.json")
    _eval_results["timestamp"] = datetime.now().isoformat()
    with open(path, "w") as f:
        json.dump(_eval_results, f, indent=2, default=str)
    print(f"\n[Eval] Results saved to {path}")


def evaluate_fake_news():
    print("\n" + "=" * 60)
    print("  EVALUATION: Fake News Detection")
    print("=" * 60)

    try:
        from sklearn.metrics import (
            accuracy_score, precision_recall_fscore_support,
            confusion_matrix, roc_curve, auc, classification_report
        )
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        from datasets import load_dataset
    except ImportError as e:
        print(f"[WARNING] Missing deps for fake_news eval: {e}")
        _eval_results["fake_news"] = {"error": str(e)}
        return

    # --- RoBERTa evaluation ---
    print("[1/3] Evaluating RoBERTa on LIAR test set...")
    roberta_results = {}
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        model_path = os.path.join(os.path.dirname(__file__), "fake_news", "saved_model")
        model_name = model_path if os.path.exists(os.path.join(model_path, "config.json")) else "roberta-base"

        dataset = load_dataset("liar", trust_remote_code=True, split="test")
        label_map = {"pants-fire": 0, "false": 0, "barely-true": 0, "half-true": 1, "mostly-true": 1, "true": 1}

        texts = dataset["statement"][:200]
        y_true_rb = [label_map.get(l, 1) for l in dataset["label"][:200]]

        classifier = pipeline("text-classification", model=model_name, tokenizer=model_name, max_length=256, truncation=True)
        predictions = classifier(texts)
        y_pred_rb = [1 if p["label"] in ("LABEL_1", "POSITIVE", "real") else 0 for p in predictions]
        y_score_rb = [p["score"] for p in predictions]

        acc = accuracy_score(y_true_rb, y_pred_rb)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true_rb, y_pred_rb, average="binary", zero_division=0)
        cm = confusion_matrix(y_true_rb, y_pred_rb)

        roberta_results = {"accuracy": round(acc, 4), "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Fake", "Real"], yticklabels=["Fake", "Real"])
        plt.title("Confusion Matrix — RoBERTa (LIAR)")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "charts", "confusion_fake_news_roberta.png"), dpi=150)
        plt.close()

        fpr, tpr, _ = roc_curve(y_true_rb, y_score_rb)
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(5, 4))
        plt.plot(fpr, tpr, label=f"RoBERTa (AUC={roc_auc:.3f})", linewidth=2)
        plt.plot([0, 1], [0, 1], "k--", alpha=0.3)
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve — Fake News Detection")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "charts", "roc_fake_news.png"), dpi=150)
        plt.close()

        print(f"  RoBERTa — Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f}")
    except Exception as e:
        print(f"  RoBERTa eval failed: {e}")
        roberta_results = {"error": str(e)}

    # --- Keyword baseline ---
    print("[2/3] Evaluating Keyword-based baseline...")
    keyword_results = {}
    try:
        from ml_models.fake_news.predict import predict_fake_news

        dataset = load_dataset("liar", trust_remote_code=True, split="test")
        label_map = {"pants-fire": 0, "false": 0, "barely-true": 0, "half-true": 1, "mostly-true": 1, "true": 1}

        texts = dataset["statement"][:200]
        y_true = [label_map.get(l, 1) for l in dataset["label"][:200]]

        y_pred_kw = []
        for t in texts:
            result = predict_fake_news(t)
            y_pred_kw.append(1 if result["label"] == "real" else 0)

        acc_kw = accuracy_score(y_true, y_pred_kw)
        prec_kw, rec_kw, f1_kw, _ = precision_recall_fscore_support(y_true, y_pred_kw, average="binary", zero_division=0)

        keyword_results = {"accuracy": round(acc_kw, 4), "precision": round(prec_kw, 4), "recall": round(rec_kw, 4), "f1": round(f1_kw, 4)}
        print(f"  Keyword — Acc: {acc_kw:.4f} | Prec: {prec_kw:.4f} | Rec: {rec_kw:.4f} | F1: {f1_kw:.4f}")
    except Exception as e:
        print(f"  Keyword eval failed: {e}")
        keyword_results = {"error": str(e)}

    _eval_results["fake_news"] = {
        "roberta": roberta_results,
        "keyword_baseline": keyword_results,
    }


def evaluate_sentiment():
    print("\n" + "=" * 60)
    print("  EVALUATION: Sentiment Analysis")
    print("=" * 60)

    try:
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, roc_curve, auc
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        from datasets import load_dataset
    except ImportError as e:
        print(f"[WARNING] Missing deps: {e}")
        _eval_results["sentiment"] = {"error": str(e)}
        return

    print("[1/4] Loading SST-2...")
    dataset = load_dataset("glue", "sst2", split="validation")
    texts = dataset["sentence"][:300]
    y_true = dataset["label"][:300]

    # --- DistilBERT ---
    print("[2/4] Evaluating DistilBERT...")
    dist_results = {}
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        model_path = os.path.join(os.path.dirname(__file__), "sentiment", "saved_model")
        model_name = model_path if os.path.exists(os.path.join(model_path, "config.json")) else "distilbert-base-uncased-finetuned-sst-2-english"

        classifier = pipeline("text-classification", model=model_name, tokenizer=model_name, max_length=256, truncation=True)
        predictions = classifier(texts[:200])
        y_pred_db = [1 if p["label"] in ("LABEL_1", "POSITIVE") else 0 for p in predictions]
        y_score_db = [p["score"] for p in predictions]

        acc = accuracy_score(y_true[:200], y_pred_db)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true[:200], y_pred_db, average="binary", zero_division=0)

        dist_results = {"accuracy": round(acc, 4), "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}
        print(f"  DistilBERT — Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f}")

        cm = confusion_matrix(y_true[:200], y_pred_db)
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Negative", "Positive"], yticklabels=["Negative", "Positive"])
        plt.title("Confusion Matrix — DistilBERT (SST-2)")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "charts", "confusion_sentiment_distilbert.png"), dpi=150)
        plt.close()
    except Exception as e:
        print(f"  DistilBERT eval failed: {e}")
        dist_results = {"error": str(e)}

    # --- VADER ---
    print("[3/4] Evaluating VADER baseline...")
    vader_results = {}
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        vader = SentimentIntensityAnalyzer()

        y_pred_vd = []
        for t in texts:
            scores = vader.polarity_scores(t)
            y_pred_vd.append(1 if scores["compound"] >= 0.05 else 0)

        acc_vd = accuracy_score(y_true, y_pred_vd)
        prec_vd, rec_vd, f1_vd, _ = precision_recall_fscore_support(y_true, y_pred_vd, average="binary", zero_division=0)

        vader_results = {"accuracy": round(acc_vd, 4), "precision": round(prec_vd, 4), "recall": round(rec_vd, 4), "f1": round(f1_vd, 4)}
        print(f"  VADER — Acc: {acc_vd:.4f} | Prec: {prec_vd:.4f} | Rec: {rec_vd:.4f} | F1: {f1_vd:.4f}")

        cm_vd = confusion_matrix(y_true, y_pred_vd)
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm_vd, annot=True, fmt="d", cmap="Oranges", xticklabels=["Negative", "Positive"], yticklabels=["Negative", "Positive"])
        plt.title("Confusion Matrix — VADER (SST-2)")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "charts", "confusion_sentiment_vader.png"), dpi=150)
        plt.close()
    except Exception as e:
        print(f"  VADER eval failed: {e}")
        vader_results = {"error": str(e)}

    # --- ROC comparison ---
    print("[4/4] Generating ROC comparison...")
    try:
        from sklearn.metrics import roc_curve, auc

        plt.figure(figsize=(6, 5))

        y_score_vd = []
        vader = __import__("vaderSentiment.vaderSentiment", fromlist=["SentimentIntensityAnalyzer"]).SentimentIntensityAnalyzer()
        for t in texts:
            y_score_vd.append((vader.polarity_scores(t)["compound"] + 1) / 2)

        fpr_vd, tpr_vd, _ = roc_curve(y_true, y_score_vd)
        roc_auc_vd = auc(fpr_vd, tpr_vd)
        plt.plot(fpr_vd, tpr_vd, label=f"VADER (AUC={roc_auc_vd:.3f})", linewidth=2, color="orange")

        if y_score_db and len(y_score_db) >= 200:
            fpr_db, tpr_db, _ = roc_curve(y_true[:200], y_score_db)
            roc_auc_db = auc(fpr_db, tpr_db)
            plt.plot(fpr_db, tpr_db, label=f"DistilBERT (AUC={roc_auc_db:.3f})", linewidth=2, color="blue")

        plt.plot([0, 1], [0, 1], "k--", alpha=0.3)
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve — Sentiment Analysis Comparison")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "charts", "roc_sentiment.png"), dpi=150)
        plt.close()
    except Exception as e:
        print(f"  ROC failed: {e}")

    _eval_results["sentiment"] = {
        "distilbert": dist_results,
        "vader_baseline": vader_results,
    }


def generate_comparison_table():
    print("\n" + "=" * 60)
    print("  MODEL COMPARISON TABLE")
    print("=" * 60)
    print()

    rows = [
        ("Fake News", "RoBERTa (LIAR)", "Deep learning", _eval_results.get("fake_news", {}).get("roberta", {}).get("accuracy", "—"), _eval_results.get("fake_news", {}).get("roberta", {}).get("f1", "—")),
        ("Fake News", "Keyword Baseline", "Rule-based", _eval_results.get("fake_news", {}).get("keyword_baseline", {}).get("accuracy", "—"), _eval_results.get("fake_news", {}).get("keyword_baseline", {}).get("f1", "—")),
        ("Sentiment", "DistilBERT (SST-2)", "Deep learning", _eval_results.get("sentiment", {}).get("distilbert", {}).get("accuracy", "—"), _eval_results.get("sentiment", {}).get("distilbert", {}).get("f1", "—")),
        ("Sentiment", "VADER Baseline", "Lexicon-based", _eval_results.get("sentiment", {}).get("vader_baseline", {}).get("accuracy", "—"), _eval_results.get("sentiment", {}).get("vader_baseline", {}).get("f1", "—")),
        ("Topic Modeling", "BERTopic (20 Newsgroups)", "Embedding", _eval_results.get("topic_modeling", {}).get("n_topics", "—"), _eval_results.get("topic_modeling", {}).get("nmi", "—")),
    ]

    header = "{:<18} {:<28} {:<18} {:<12} {:<12}".format("Task", "Model", "Type", "Accuracy", "F1/Score")
    sep = "-" * 95
    print(header)
    print(sep)
    for task, model, mtype, acc, f1 in rows:
        acc_str = f"{acc}" if isinstance(acc, str) else f"{acc:.4f}" if isinstance(acc, float) else "—"
        f1_str = f"{f1}" if isinstance(f1, str) else f"{f1:.4f}" if isinstance(f1, float) else "—"
        print(f"{task:<18} {model:<28} {mtype:<18} {acc_str:<12} {f1_str:<12}")

    md_path = os.path.join(RESULTS_DIR, "model_comparison.md")
    with open(md_path, "w") as f:
        f.write("# Model Comparison\n\n")
        f.write("| Task | Model | Type | Accuracy | F1 Score |\n")
        f.write("|------|-------|------|----------|----------|\n")
        for task, model, mtype, acc, f1 in rows:
            acc_str = f"{acc}" if isinstance(acc, str) else f"{acc:.4f}" if isinstance(acc, float) else "—"
            f1_str = f"{f1}" if isinstance(f1, str) else f"{f1:.4f}" if isinstance(f1, float) else "—"
            f.write(f"| {task} | {model} | {mtype} | {acc_str} | {f1_str} |\n")
        f.write(f"\n*Generated: {datetime.now().isoformat()}*\n")
    print(f"\n  Markdown table saved to {md_path}")

    _eval_results["comparison_table"] = [
        {"task": task, "model": model, "type": mtype, "accuracy": acc, "f1": f1}
        for task, model, mtype, acc, f1 in rows
    ]


def evaluate_topic_modeling():
    print("\n" + "=" * 60)
    print("  EVALUATION: Topic Modeling")
    print("=" * 60)
    print("[INFO] Topic model evaluation is done during training (NMI, outlier ratio, etc.)")
    _eval_results["topic_modeling"] = {"evaluation": "See training_results.json for NMI score and topic counts"}


def main():
    parser = argparse.ArgumentParser(description="Evaluate all ML models for SocialPulse AI")
    parser.add_argument("--model", choices=["all", "fake_news", "sentiment", "topic"], default="all")
    parser.add_argument("--compare", action="store_true", help="Only generate comparison table")
    args = parser.parse_args()

    print("=" * 60)
    print("  SocialPulse AI — Model Evaluation Suite")
    print("=" * 60)

    if args.compare:
        if args.model == "all":
            try:
                evaluate_fake_news()
            except Exception as e:
                print(f"Fake news eval failed: {e}")
            try:
                evaluate_sentiment()
            except Exception as e:
                print(f"Sentiment eval failed: {e}")
            evaluate_topic_modeling()
        generate_comparison_table()
        save_eval()
        return

    if args.model in ("all", "fake_news"):
        try:
            evaluate_fake_news()
        except Exception as e:
            print(f"[WARNING] Fake news eval failed: {e}")

    if args.model in ("all", "sentiment"):
        try:
            evaluate_sentiment()
        except Exception as e:
            print(f"[WARNING] Sentiment eval failed: {e}")

    if args.model in ("all", "topic"):
        evaluate_topic_modeling()

    generate_comparison_table()
    save_eval()

    print("\n" + "=" * 60)
    print("  Evaluation complete! Charts saved to results/charts/")
    print("=" * 60)


if __name__ == "__main__":
    main()
