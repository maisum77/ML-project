# SocialPulse AI

Real-Time Misinformation & Trend Analyzer

## Overview

SocialPulse AI is a machine learning-powered platform that aggregates real-time data from Reddit and X (Twitter) to detect hot topics, analyze sentiment, identify fake vs. real news, and surface emerging trends through an intuitive analytics dashboard.

## Features

- **Real-time Data Collection** - Reddit (PRAW) and X/Twitter (Tweepy) APIs with 15-minute polling
- **Fake News Detection** - Fine-tuned RoBERTa model for binary classification with confidence scores
- **Sentiment Analysis** - DistilBERT (3-class) with VADER fallback for lightweight processing
- **Topic Modeling** - BERTopic for dynamic embedding-based topic clustering
- **Fact-Check Verification** - Google Fact Check Tools API + ClaimBuster integration
- **Analytics Dashboard** - Live trending topics, sentiment charts, and searchable post explorer
- **REST API** - FastAPI backend with rate limiting and API key authentication

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Frontend | Next.js + React + Chart.js |
| Database | MongoDB |
| Task Queue | Celery + Redis |
| ML Models | RoBERTa, DistilBERT, BERTopic, VADER |
| NLP | spaCy, HuggingFace Transformers |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)
- Redis
- Docker (optional, for MongoDB + Redis)

### 1. Clone & Setup

```bash
cd "ML project"
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start Infrastructure

```bash
docker-compose up -d
```

### 4. Run Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Start Data Collection

```bash
python -c "from data_collection.scheduler import start_scheduler; start_scheduler()"
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/trending | Get trending topics |
| GET | /api/v1/trending/realtime | Real-time trending (last N hours) |
| GET | /api/v1/sentiment/{topic} | Sentiment for a specific topic |
| GET | /api/v1/sentiment/overall | Overall sentiment breakdown |
| POST | /api/v1/classify | Classify text as fake/real + sentiment |
| GET | /api/v1/feed | Get post feed with filters |
| GET | /api/v1/export | Export data as JSON or CSV |

## Project Structure

```
ML project/
├── backend/              # FastAPI backend
│   └── app/
│       ├── api/          # API routes
│       ├── core/         # Config, database, security
│       ├── schemas/      # Pydantic models
│       └── services/     # Business logic
├── data_collection/      # Reddit + Twitter data collectors
├── data_processing/      # Text preprocessing pipeline
├── ml_models/            # ML model training & inference
│   ├── fake_news/        # RoBERTa fake news classifier
│   ├── sentiment/        # DistilBERT sentiment analyzer
│   └── topic_modeling/   # BERTopic topic clustering
├── fact_check/           # Google Fact Check + ClaimBuster
├── frontend/             # Next.js dashboard
├── tests/                # Test suite
├── scripts/              # Utility scripts
└── deployment/           # Docker & deployment configs
```

## API Keys Required

- **Reddit**: Create app at https://www.reddit.com/prefs/apps
- **X/Twitter**: Developer account at https://developer.twitter.com
- **Google Fact Check**: Enable API at Google Cloud Console
- **ClaimBuster**: Register at https://claimbuster.idaholab.ai

## License

MIT
