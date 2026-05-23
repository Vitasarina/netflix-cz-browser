import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Any, cast
from pydantic import BaseModel, field_validator
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore

from .config import settings
from .database import get_db, init_db, sync_trending_data, SessionLocal
from .models import Title

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def schedule_sync() -> None:
    """Schedule daily sync"""
    trigger = CronTrigger(hour=settings.SYNC_HOUR, minute=settings.SYNC_MINUTE)
    scheduler.add_job(sync_trending_data, trigger, id="sync_trending")
    scheduler.start()
    logger.info(f"Scheduler started: daily sync at {settings.SYNC_HOUR}:{settings.SYNC_MINUTE:02d}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown"""
    init_db()
    schedule_sync()

    # Check if database is empty
    db = SessionLocal()
    try:
        count = db.query(Title).count()
        if count == 0:
            logger.info("Database is empty, performing initial sync...")
            if sync_trending_data():
                logger.info("Initial sync completed successfully")
            else:
                logger.warning("Initial sync failed. API keys may be missing.")
    finally:
        db.close()

    yield

    scheduler.shutdown()


app = FastAPI(title="Netflix CZ Trending Browser", lifespan=lifespan)

# CORS middleware
origins = settings.CORS_ORIGINS
if origins and origins != ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class TitleResponse(BaseModel):
    id: int
    tmdb_id: Optional[str]
    title: str
    year: Optional[int]
    type: str
    rating: Optional[float]
    popularity_rank: int
    poster_url: Optional[str]
    overview: Optional[str]
    trailer_url: Optional[str]
    genres: Optional[List[str]]
    position: int
    scraped_at: datetime

    class Config:
        from_attributes = True

    @field_validator("genres", mode="before")
    @classmethod
    def deserialize_genres(cls, v: Any) -> Optional[List[str]]:
        if v is None:
            return None
        if isinstance(v, list):
            return cast(List[str], v)
        if isinstance(v, str):
            try:
                return cast(List[str], json.loads(v))
            except (json.JSONDecodeError, ValueError):
                return None
        return None


class TitleDetailResponse(TitleResponse):
    pass


@app.get("/api/trending", response_model=List[TitleResponse])
async def get_trending(type: Optional[str] = None, db: Session = Depends(get_db)) -> List[Any]:
    """Get list of trending titles"""
    query = db.query(Title)

    if type:
        if type not in ["movie", "series"]:
            raise HTTPException(status_code=400, detail="Invalid type. Use 'movie' or 'series'")
        query = query.filter(Title.type == type)

    titles = query.order_by(Title.position).all()
    return titles


@app.get("/api/trending/{title_id}", response_model=TitleDetailResponse)
async def get_trending_detail(title_id: int, db: Session = Depends(get_db)) -> Any:
    """Get detail of a specific title"""
    title = db.query(Title).filter(Title.id == title_id).first()

    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    return title


@app.post("/api/sync")
async def manual_sync() -> Dict[str, Any]:
    """Manually trigger sync"""
    if not settings.api_keys_available:
        logger.error("API keys not configured")
        return {
            "status": "error",
            "message": "API keys (TMDB_API_KEY, YOUTUBE_API_KEY) are not configured. Set them in .env file.",
            "code": 503
        }

    if await sync_trending_data_async():
        return {"status": "success", "message": "Sync completed successfully"}
    else:
        return {"status": "error", "message": "Sync failed"}


async def sync_trending_data_async() -> bool:
    """Async wrapper for sync_trending_data"""
    return sync_trending_data()


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_keys_configured": settings.api_keys_available,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
