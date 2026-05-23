import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/netflix.db")
    SYNC_HOUR = int(os.getenv("SYNC_HOUR", "6"))
    SYNC_MINUTE = int(os.getenv("SYNC_MINUTE", "0"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    @property
    def api_keys_available(self):
        return bool(self.TMDB_API_KEY and self.YOUTUBE_API_KEY)


settings = Settings()
