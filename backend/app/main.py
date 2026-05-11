from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.api.router import router as api_router
from backend.app.core.config import get_settings
from backend.app.core.database import init_db, seed_demo_data

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_demo_data()
    yield

app = FastAPI(
    title="SocialPulse AI",
    description="Real-Time Misinformation & Trend Analyzer API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "SocialPulse AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
