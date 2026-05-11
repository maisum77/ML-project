from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.router import router as api_router
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="SocialPulse AI",
    description="Real-Time Misinformation & Trend Analyzer",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    from backend.app.core.database import init_db, seed_demo_data
    await init_db()
    await seed_demo_data()


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
