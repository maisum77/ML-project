#!/bin/bash

echo "========================================"
echo "  SocialPulse AI - Starting Services"
echo "========================================"
echo

echo "[1/4] Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker."
    exit 1
fi

echo "[2/4] Starting MongoDB and Redis..."
docker-compose up -d

echo "[3/4] Starting Backend (port 8000)..."
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 &

echo "[4/4] Starting Frontend (port 3000)..."
cd frontend && npm run dev &

echo
echo "========================================"
echo "  Services Started!"
echo "========================================"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:3000"
echo "========================================"
echo
echo "To start data collection, run:"
echo "  python -c 'from data_collection.scheduler import start_scheduler; start_scheduler()'"
echo
