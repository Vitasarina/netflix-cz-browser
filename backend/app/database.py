import os
import time
from typing import Generator
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Title, get_engine, get_session_local
from .config import settings
from .scrapers import TMDbAPI, YouTubeAPI
import logging

logger = logging.getLogger(__name__)

engine = get_engine(settings.DATABASE_URL)
SessionLocal = get_session_local(engine)


def init_db() -> None:
    """Initialize database"""
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_trending_data() -> bool:
    """Fetch and sync trending data from TMDB Discover API and external APIs"""
    if not settings.api_keys_available:
        logger.warning("API keys not configured. Skipping sync. Please set TMDB_API_KEY and YOUTUBE_API_KEY in .env")
        return False

    logger.info("Starting trending data sync...")
    db = SessionLocal()

    try:
        tmdb = TMDbAPI(settings.TMDB_API_KEY)
        youtube = YouTubeAPI(settings.YOUTUBE_API_KEY)

        # Clear existing data
        db.query(Title).delete()
        db.commit()

        all_titles = []

        # Get trending movies from TMDB Discover API
        logger.info("Fetching trending movies from TMDB Discover API...")
        movies = tmdb.get_trending("movie")
        for movie in movies:
            logger.info(f"Processing movie: {movie['title']}")
            trailer = youtube.search_trailer(movie["title"], movie.get("year"))
            if trailer:
                movie["trailer_url"] = trailer
            movie["type"] = "movie"
            all_titles.append(movie)
            time.sleep(0.5)

        # Get trending series from TMDB Discover API
        logger.info("Fetching trending series from TMDB Discover API...")
        series = tmdb.get_trending("tv")
        for serie in series:
            logger.info(f"Processing series: {serie['title']}")
            trailer = youtube.search_trailer(serie["title"], serie.get("year"))
            if trailer:
                serie["trailer_url"] = trailer
            serie["type"] = "series"
            all_titles.append(serie)
            time.sleep(0.5)

        # Save to database
        for title_data in all_titles:
            title = Title(
                tmdb_id=str(title_data.get("tmdb_id", "")),
                title=title_data["title"],
                year=title_data.get("year"),
                type=title_data["type"],
                rating=title_data.get("rating"),
                popularity_rank=0,
                poster_url=title_data.get("poster_url"),
                overview=title_data.get("overview"),
                trailer_url=title_data.get("trailer_url"),
                genres=title_data.get("genres"),
                position=title_data.get("position")
            )
            db.add(title)

        db.commit()
        logger.info(f"Successfully synced {len(all_titles)} titles")
        return True

    except (requests.RequestException, SQLAlchemyError, ValueError) as e:
        logger.error(f"Error during sync: {e}")
        db.rollback()
        return False
    finally:
        db.close()
