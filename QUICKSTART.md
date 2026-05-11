# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Start MongoDB & Redis

```bash
docker-compose up -d
```

Or use local installations:
- MongoDB: `mongod`
- Redis: `redis-server`

### Step 3: Configure API Keys

Edit `.env` and add your API credentials:

```
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
X_BEARER_TOKEN=your_token
MONGODB_URI=mongodb://localhost:27017
```

### Step 4: Start Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see the API.

### Step 5: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000 for the dashboard.

### Step 6: Start Data Collection

```bash
python -c "from data_collection.scheduler import start_scheduler; start_scheduler()"
```

Data will be collected every 15 minutes from Reddit and Twitter.

## Test the API

```bash
# Health check
curl http://localhost:8000/health

# Classify text
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "AI will replace all jobs by 2030"}'

# Get trending
curl http://localhost:8000/api/v1/trending
```

## Troubleshooting

- **MongoDB connection error**: Make sure Docker is running or MongoDB is installed
- **Reddit API error**: Verify your client ID and secret in .env
- **spaCy error**: Run `python -m spacy download en_core_web_sm`
- **Port already in use**: Change port in uvicorn command
