@echo off
echo ========================================
echo   SocialPulse AI - Starting Services
echo ========================================
echo.

echo [1/4] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo [2/4] Starting MongoDB and Redis...
docker-compose up -d
if %errorlevel% neq 0 (
    echo Failed to start Docker containers.
    pause
    exit /b 1
)

echo [3/4] Starting Backend (port 8000)...
start "SocialPulse Backend" cmd /k "uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"

echo [4/4] Starting Frontend (port 3000)...
cd frontend
start "SocialPulse Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:3000
echo ========================================
echo.
echo To start data collection, run:
echo   python -c "from data_collection.scheduler import start_scheduler; start_scheduler()"
echo.
pause
