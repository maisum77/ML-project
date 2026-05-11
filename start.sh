#!/bin/bash

echo "========================================"
echo "  SocialPulse AI - Starting Services"
echo "========================================"
echo

echo "[1/3] Installing dependencies..."
pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo "[2/3] Starting Backend (port 8000)..."
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 &

echo "[3/3] Starting Frontend (port 3000)..."
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
echo "Serverless deployment: sam deploy --guided"
echo "DynamoDB tables: sam deploy creates them automatically"
echo
