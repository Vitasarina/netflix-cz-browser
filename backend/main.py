import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Netflix CZ Browser API",
    description="API pro Netflix CZ Trending Browser",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "netflix-cz-browser"}


@app.get("/health")
def health():
    tmdb_key = os.getenv("TMDB_API_KEY", "")
    youtube_key = os.getenv("YOUTUBE_API_KEY", "")
    return {
        "status": "healthy",
        "tmdb_configured": bool(tmdb_key),
        "youtube_configured": bool(youtube_key),
    }


# TODO: Backend developer adds routes here
# e.g. /trending, /titles/{id}, /sync
