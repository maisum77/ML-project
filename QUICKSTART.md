# Quick Start Guide

## Local Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Configure Environment

Set your credentials in `.env`:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
X_BEARER_TOKEN=your_token
```

### Step 3: Start Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for Swagger UI.

### Step 4: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000 for the dashboard.

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Classify text (on-demand, no prior data needed)
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "AI will replace all jobs by 2030"}'

# Get trending (fetches live Reddit/Twitter data)
curl http://localhost:8000/api/v1/trending
```

## Serverless Deployment

### Prerequisites
- AWS SAM CLI installed
- AWS credentials configured

### Deploy

```bash
sam build
sam deploy --guided
```

SAM creates:
- **Lambda function** `socialpulse-api-dev` (Python 3.11, 1GB RAM)
- **API Gateway HTTP API** (Serverless, pay-per-request)
- **5 DynamoDB tables** (PAY_PER_REQUEST billing)

After deployment, SAM outputs the API Gateway URL. Set it as `NEXT_PUBLIC_API_URL` in Amplify.

### Frontend Deployment

1. Push code to GitHub
2. Create AWS Amplify app → connect repo
3. Amplify auto-detects `amplify.yml` and deploys Next.js
4. Set environment variable: `NEXT_PUBLIC_API_URL` = API Gateway URL from SAM output

### Architecture

```
User → Amplify (Next.js) → API Gateway → Lambda (FastAPI)
                                            │
                              ┌─────────────┤
                              ▼             ▼
                         Reddit/Twitter  VADER Sentiment
                              │             │
                              ▼             ▼
                         DynamoDB ←──── Response
```

Every API call triggers on-demand data collection. Lambda only runs when a request comes in.

## Troubleshooting

- **DynamoDB error**: Verify AWS credentials in `.env`
- **Reddit API error**: Check `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
- **X/Twitter API error**: Check `X_BEARER_TOKEN`
- **spaCy error**: Run `python -m spacy download en_core_web_sm`
- **Lambda timeout**: First cold start may take 30-60s. Subsequent calls are fast.
