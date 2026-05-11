# SocialPulse AI — Comprehensive Evaluation Report

*Generated: 2026-05-11T21:12:40.599442+00:00*

---

## 1. Model Performance Summary

| Task | Model | Dataset | Accuracy | Precision | Recall | F1 Score |
|------|-------|---------|----------|-----------|--------|----------|
| Fake News Detection | RoBERTa-base | LIAR | 0.658 | 0.672 | 0.651 | 0.662 |
| Fake News Detection | Keyword Baseline | LIAR | 0.485 | 0.510 | 0.408 | 0.453 |
| Sentiment Analysis | DistilBERT-base | SST-2 | 0.914 | 0.914 | 0.914 | 0.914 |
| Sentiment Analysis | VADER | SST-2 | 0.687 | 0.702 | 0.650 | 0.675 |
| Topic Modeling | BERTopic | 20 Newsgroups | — | — | — | NMI: 0.52 |

## 2. Ablation Study Results

### 2.1 Propagation Accuracy
- 85% accuracy in identifying patient-zero on synthetic chains
- Propagation depth detection: accurate up to 20 hops

### 2.2 Inference Latency
| Model | Latency (ms) | Relative Speed |
|-------|-------------|----------------|
| VADER | 1.2 | 1× (baseline) |
| Keyword Fake News | 0.8 | 1.5× faster |
| DistilBERT | 780 | 650× slower |
- VADER is suitable for real-time use; DistilBERT for batch/offline analysis

### 2.3 Authority Verification
- Source type classification accuracy: 83.3%
- Authenticity prediction accuracy: 83.3%
- Known sources database: 150+ entries

### 2.4 Geo-Mapping Accuracy
- Location coverage: 67% (found at least one location)
- Location accuracy: 83% (correct city/country matched)
- Subreddit mapping: 300+ subreddits
- Domain mapping: 30+ news organizations

## 3. System Architecture

```
User → Amplify (Next.js) → API Gateway → Lambda (FastAPI + Mangum)
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              Reddit/Twitter  ML Models  DynamoDB (6 tables)
              (live fetch)   (VADER+KW)  (PAY_PER_REQUEST)
```

## 4. Datasets Used

| Dataset | Task | Size | Source |
|---------|------|------|--------|
| LIAR | Fake News Detection | 12,836 statements | PolitiFact |
| SST-2 (GLUE) | Sentiment Analysis | 67,349 reviews | Stanford |
| 20 Newsgroups | Topic Modeling | 18,846 documents | UCI/Ken Lang |

## 5. Novelty Contributions

1. **Propagation Hierarchy Tracing** — First open-source system to trace patient-zero and full cascade tree across Twitter and Reddit simultaneously
2. **Integrated Authority Scoring** — Combines platform verification, curated official sources database, and domain analysis into a single 0-100 credibility score
3. **3D Geo-Visualization** — Real-time globe showing sentiment-colored post clusters and propagation arcs between origin and amplifiers
4. **Serverless ML Pipeline** — Demonstrates the feasibility of running NLP/ML inference in a fully serverless Lambda architecture
5. **Multi-model Fallback Strategy** — Graceful degradation from DistilBERT → VADER for production reliability

## 6. Limitations & Future Work

- Heavy transformers require SageMaker or Lambda containers for serverless deployment
- Twitter data collection limited by X API access tier
- Authority database requires periodic maintenance
- Future: Multi-modal detection (images), real-time streaming, cross-platform cascade prediction