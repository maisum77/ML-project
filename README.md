# SocialPulse AI

Real-Time Misinformation & Trend Analyzer (Serverless Architecture)

## Overview

SocialPulse AI is an on-demand platform that fetches real-time data from Reddit and X (Twitter), analyzes sentiment, detects fake news, and surfaces trends through an analytics dashboard. Built fully serverless on AWS.

## How It Works

```
User visits website
      │
      ▼
Next.js (Amplify) → API Gateway → Lambda (FastAPI)
      │                                │
      │                    ┌───────────┤
      │                    ▼           ▼
      │              Reddit/Twitter  VADER Sentiment
      │                    │           │
      │                    ▼           ▼
      │               DynamoDB    ──► Response
      │
      ▼
Dashboard renders with fresh data
```

Every API call triggers on-demand data collection + analysis. No polling, no persistent servers.

## Features

- **On-demand Data Collection** - Fetches Reddit/Twitter posts in real-time when you request
- **Sentiment Analysis** - VADER-based positive/negative/neutral classification
- **Fake News Detection** - Keyword + pattern-based classifier
- **Fact-Check Verification** - Google Fact Check Tools API + ClaimBuster
- **Analytics Dashboard** - Trending topics, sentiment charts, post explorer
- **Serverless** - API Gateway + Lambda + DynamoDB. Zero maintenance.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Frontend | Next.js + React + Chart.js |
| Database | AWS DynamoDB |
| Hosting | AWS Amplify (Frontend) + API Gateway + Lambda (Backend) |
| Sentiment | VADER |
| NLP | spaCy |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- AWS Account

### 1. Clone & Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your AWS credentials and API keys
```

### 3. Run Locally

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend && npm install && npm run dev
```

### 4. Deploy (Serverless)

```bash
# Install AWS SAM CLI
# sam build && sam deploy --guided
```

This creates:
- Lambda function (1 GB RAM, 120s timeout)
- API Gateway HTTP API
- 5 DynamoDB tables (PAY_PER_REQUEST)

### 5. Deploy Frontend

Push to GitHub → Connect to AWS Amplify → `amplify.yml` auto-deploys Next.js.

Set `NEXT_PUBLIC_API_URL` in Amplify to the API Gateway URL from SAM output.

## API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/trending | Fresh trending topics (fetches live data) |
| GET | /api/v1/trending/realtime | Real-time trending |
| GET | /api/v1/sentiment/{topic} | Sentiment for a topic |
| GET | /api/v1/sentiment/overall | Overall sentiment breakdown |
| POST | /api/v1/classify | Classify text (fake/real + sentiment) |
| GET | /api/v1/feed | Post feed with filters |
| GET | /api/v1/export | Export as JSON/CSV |

## Project Structure

```
├── backend/              # FastAPI backend
│   ├── lambda_handler.py # Mangum → Lambda entry point
│   └── app/
│       ├── api/          # API routes
│       ├── core/         # Config, DynamoDB, security
│       ├── schemas/      # Pydantic models
│       └── services/     # Business logic
├── data_collection/      # Reddit + Twitter collectors (on-demand)
├── data_processing/      # Text preprocessing (spaCy + VADER)
├── ml_models/            # ML models (VADER sentiment, keyword fake-news)
├── frontend/             # Next.js dashboard
├── template.yaml         # SAM: Lambda + API Gateway + DynamoDB
├── amplify.yml           # Amplify Hosting config
└── scripts/              # Utility scripts
```

## License

MIT
