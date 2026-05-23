"""Standalone scheduler process — runs periodic data sync jobs."""
import logging
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [scheduler] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "3600"))


def sync_now():
    """Trigger a single data sync. Backend developer implements the logic here."""
    tmdb_key = os.getenv("TMDB_API_KEY", "")
    if not tmdb_key:
        logger.warning("TMDB_API_KEY not set — skipping sync")
        return
    logger.info("Starting data sync...")
    # TODO: Backend developer adds sync logic here
    logger.info("Sync complete")


def main():
    logger.info("Scheduler started, interval=%ds", SYNC_INTERVAL_SECONDS)
    while True:
        sync_now()
        logger.info("Next sync in %d seconds", SYNC_INTERVAL_SECONDS)
        time.sleep(SYNC_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
