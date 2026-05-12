# SocialPulse AI

Real-Time Misinformation & Trend Analyzer — Serverless Architecture

## Overview

SocialPulse AI fetches real-time data from Reddit and X (Twitter), analyzes sentiment, detects misinformation, scores source authority, clusters topics, and presents everything through an interactive dashboard. Fully serverless on AWS.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           Next.js Frontend              │
                    │   (AWS Amplify · React · Chart.js)      │
                    └──────────────┬──────────────────────────┘
                                   │ HTTP
                    ┌──────────────▼──────────────────────────┐
                    │       FastAPI Backend (Lambda)           │
                    │  ┌──────────┐  ┌───────────────────────┐ │
                    │  │  API      │  │  Services              │ │
                    │  │  Routes   │  │  ┌─────────────────┐   │ │
                    │  │  /trending│  │  │ Classification   │   │ │
                    │  │  /classify│  │  │ Authority        │   │ │
                    │  │  /feed    │  │  │ Clustering       │   │ │
                    │  │  /auth    │  │  │ Sentiment        │   │ │
                    │  │  /export  │  │  │ Fact-checking     │   │ │
                    │  │  /geo     │  │  │ Auth/JWT         │   │ │
                    │  └──────────┘  │  └─────────────────┘   │ │
                    └──────┬─────────┴────────────────────────┘
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                 ▼
        ┌──────────┐ ┌──────────┐    ┌──────────────┐
        │ DynamoDB │ │ Reddit   │    │ X/Twitter    │
        │ (7 tables│ │ API      │    │ API (OAuth1) │
        │  + GSI)  │ │          │    │              │
        └──────────┘ └──────────┘    └──────────────┘
                           │                 │
              ┌────────────▼─────────────────▼──┐
              │   Google Fact Check · ClaimBuster │
              └──────────────────────────────────┘
```

## Features

### Core Analysis
- **Fake News Detection** — Multi-signal classifier analyzing linguistic patterns, emotional language, source authority, entity extraction, topic modeling, and fact-check verification to produce a composite verdict (real/needs_verification/likely_unreliable) with risk level and confidence
- **Sentiment Analysis** — VADER-based positive/negative/neutral classification with timeline tracking
- **Source Authority Scorecard** — Classifies sources as official/journalist/organization/public and calculates authority scores (0-100) with verification bonuses
- **Topic Clustering** — Keyword co-occurrence grouping organizes posts into topic clusters with engagement metrics, sentiment distribution, and similarity scoring
- **Fact-Check Integration** — Google Fact Check Tools API + ClaimBuster for automated claim verification

### Interactive Tools
- **Text Classifier** — Analyze any text with detailed breakdown: verdict, risk level, linguistic signals, emotional language, entities, topics, and fact-check matches
- **Topic Comparison** — Compare 2-4 topics side-by-side across post counts, engagement, authority, and sentiment
- **Report Export** — Download comprehensive analysis reports with all metrics
- **Propagation Tracing** — Trace how information spreads across platforms
- **Globe Visualization** — See geographic distribution of discussions

### User Features
- **Authentication** — JWT-based register/login with encrypted passwords
- **Saved Analyses** — Store and revisit past classifications
- **Keyword Alerts** — Set monitoring keywords with notification badge
- **User Dashboard** — Profile, saved analyses, and keyword management
- **Dark Mode** — Toggle between light/dark themes with persistence

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) + Mangum (Lambda) |
| Frontend | Next.js 14 + React + Chart.js + Recharts |
| Database | AWS DynamoDB (7 tables with GSIs) |
| Auth | JWT + SHA256 + DynamoDB Users table |
| Hosting | AWS Amplify (Frontend) + API Gateway + Lambda (Backend) |
| NLP | spaCy + VADER |
| Fact-Check | Google Fact Check Tools API + ClaimBuster |
| CI/CD | GitHub Actions |

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- AWS credentials configured

### 1. Clone & Setup

```bash
git clone <repo-url> && cd sentiment-analysis
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_sm
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your AWS credentials and API keys
```

### 3. Create DynamoDB Tables

```bash
python3 scripts/create_dynamodb_tables.py
```

### 4. Run Locally

Backend:
```bash
python3 -m uvicorn backend.app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend && npm install && npm run dev
```

Or use the startup script:
```bash
./start.sh
```

### 5. Deploy (Serverless)

```bash
sam build && sam deploy --guided
```

This creates:
- Lambda function (1 GB RAM, 120s timeout)
- API Gateway HTTP API
- 7 DynamoDB tables (PAY_PER_REQUEST)

Push frontend to GitHub → Connect to AWS Amplify → `amplify.yml` auto-deploys.

Set `NEXT_PUBLIC_API_URL` in Amplify to the API Gateway URL.

## API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /api/v1/trending | Trending topics |
| GET | /api/v1/trending/realtime | Real-time trending window |
| GET | /api/v1/trending/clusters | Topic clusters |
| GET | /api/v1/trending/compare | Compare 2+ topics |
| GET | /api/v1/sentiment/{topic} | Sentiment for a topic |
| GET | /api/v1/sentiment/overall | Overall sentiment |
| POST | /api/v1/classify | Classify text (basic) |
| POST | /api/v1/classify/detailed | Full multi-signal classification |
| GET | /api/v1/feed | Post feed with filters |
| GET | /api/v1/export | Export data (JSON/CSV) |
| GET | /api/v1/export/report | Download analysis report |
| GET | /api/v1/authority/scorecard | Source authority dashboard |
| GET | /api/v1/authority/check | Check source authority |
| GET | /api/v1/geo | Geographic distribution |
| GET | /api/v1/geo/globe | Globe visualization data |
| GET | /api/v1/propagation | Trace information spread |
| POST | /api/v1/auth/register | Register new user |
| POST | /api/v1/auth/login | Login |
| GET | /api/v1/auth/me | Get current user profile |
| POST | /api/v1/auth/save-analysis | Save a classification |
| POST | /api/v1/auth/alerts | Add keyword alert |
| DELETE | /api/v1/auth/alerts/{keyword} | Remove keyword alert |
| GET | /api/v1/auth/notifications | Get alert notifications |

Interactive docs available at `/docs` when running locally.

## Project Structure

```
├── backend/
│   ├── lambda_handler.py          # Mangum → Lambda entry point
│   └── app/
│       ├── api/                   # API routes
│       │   ├── auth.py            # JWT register/login/alerts
│       │   ├── authority.py       # Source authority
│       │   ├── classify.py        # Text classification
│       │   ├── export.py          # Data export + report
│       │   ├── feed.py            # Post feed
│       │   ├── geo.py             # Geographic data
│       │   ├── propagation.py     # Info spread tracing
│       │   ├── sentiment.py       # Sentiment analysis
│       │   └── trending.py         # Trends + clusters
│       ├── core/                  # Config, DynamoDB, security
│       ├── schemas/               # Pydantic models
│       └── services/              # Business logic
│           ├── auth_service.py     # JWT auth, users, alerts
│           ├── authority_service.py # Source authority scoring
│           ├── classification_service.py # Multi-signal detection
│           └── clustering_service.py # Topic clustering + comparison
├── data_collection/               # Reddit + Twitter collectors
├── data_processing/                # Text preprocessing
├── ml_models/                     # VADER sentiment, keyword detection
├── fact_check/                    # Google Fact Check + ClaimBuster
├── frontend/
│   ├── app/page.tsx               # Main app (11 tabs)
│   ├── components/                # React components
│   │   ├── TextClassifier.tsx      # Interactive classifier
│   │   ├── TopicClusters.tsx       # Topic clustering view
│   │   ├── TopicComparison.tsx      # Side-by-side comparison
│   │   ├── SourceScorecard.tsx      # Authority dashboard
│   │   ├── ReportExport.tsx        # Report download
│   │   ├── NotificationBadge.tsx   # Alert notifications
│   │   ├── AuthForm.tsx            # Login/register
│   │   ├── UserDashboard.tsx       # User profile + alerts
│   │   └── ...                    # Charts, feed, globe, etc.
│   └── lib/
│       ├── api.ts                 # API client
│       └── auth.tsx                # Auth context provider
├── tests/
│   ├── test_classification.py     # Classification unit tests
│   ├── test_authority.py          # Authority scoring tests
│   └── test_clustering.py         # Clustering service tests
├── scripts/
│   ├── create_dynamodb_tables.py  # Provision all 7 DynamoDB tables
│   ├── demo.py                    # Demo script for presentations
│   └── validate_apis.py           # Verify all API credentials
├── template.yaml                  # SAM: Lambda + API Gateway + DynamoDB
├── amplify.yml                    # Amplify Hosting config
├── .github/workflows/ci.yml       # GitHub Actions CI
└── pytest.ini                     # Test configuration
```

## DynamoDB Tables

| Table | Key | Purpose |
|-------|-----|---------|
| socialpulse_raw_posts | id (PK) | Incoming Reddit/Twitter posts |
| socialpulse_cleaned_posts | id (PK) | Processed/cleaned posts |
| socialpulse_trends | topic_id (PK) | Trending topic data |
| socialpulse_sentiment | id (PK) | Sentiment analysis results |
| socialpulse_fact_checks | id (PK) | Fact-check verification cache |
| socialpulse_propagation | id (PK) | Propagation tracing data |
| socialpulse_users | username (PK) | User accounts, analyses, alerts |

## Testing

```bash
pip3 install pytest
python3 -m pytest tests/ -v
```

## Demo

```bash
python3 scripts/demo.py --api-url http://localhost:8000
```

## License

MIT