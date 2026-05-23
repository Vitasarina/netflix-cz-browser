import os
from typing import Generator
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Title, get_engine, get_session_local
from .config import settings
from .scrapers import FlixPatrolScraper, TMDbAPI, YouTubeAPI
import logging
import time

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
    """Fetch and sync trending data from FlixPatrol and external APIs"""
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

        # Scrape movies
        logger.info("Scraping movies from FlixPatrol...")
        movies = FlixPatrolScraper.scrape_movies()
        for movie in movies:
            logger.info(f"Enriching movie: {movie['title']}")
            enriched = tmdb.enrich_title(movie["title"], None, "movie")
            trailer = youtube.search_trailer(movie["title"], enriched.get("year"))
            if trailer:
                enriched["trailer_url"] = trailer
            enriched["position"] = movie["position"]
            enriched["type"] = "movie"
            all_titles.append(enriched)
            time.sleep(0.5)

        # Scrape series
        logger.info("Scraping series from FlixPatrol...")
        series = FlixPatrolScraper.scrape_series()
        for serie in series:
            logger.info(f"Enriching series: {serie['title']}")
            enriched = tmdb.enrich_title(serie["title"], None, "tv")
            trailer = youtube.search_trailer(serie["title"], enriched.get("year"))
            if trailer:
                enriched["trailer_url"] = trailer
            enriched["position"] = serie["position"]
            enriched["type"] = "series"
            all_titles.append(enriched)
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
