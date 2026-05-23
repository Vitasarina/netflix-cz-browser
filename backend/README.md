# Netflix CZ Trending Browser — Backend

FastAPI backend for Netflix CZ Trending Browser with FlixPatrol scraper, TMDb & YouTube integration, and APScheduler.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- **TMDB_API_KEY**: Get from [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
- **YOUTUBE_API_KEY**: Get from [Google Cloud Console](https://console.cloud.google.com/) (enable YouTube Data API v3, create API key under Credentials)

Example `.env`:
```
TMDB_API_KEY=your_api_key_here
YOUTUBE_API_KEY=your_youtube_key_here
DATABASE_URL=sqlite:///./data/netflix.db
SYNC_HOUR=6
SYNC_MINUTE=0
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Run the Server

```bash
python -m uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

## API Endpoints

### GET /api/trending
Returns list of trending titles.

**Query parameters:**
- `type`: Filter by type (`movie` or `series`)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Movie Title",
    "year": 2024,
    "type": "movie",
    "rating": 8.5,
    "popularity_rank": 0,
    "poster_url": "https://...",
    "overview": "Description...",
    "trailer_url": "https://www.youtube.com/embed/...",
    "genres": "[\"Action\", \"Drama\"]",
    "position": 1,
    "scraped_at": "2024-05-23T13:49:06Z"
  }
]
```

### GET /api/trending/{id}
Returns detail of a specific title.

### POST /api/sync
Manually trigger a data sync from FlixPatrol, TMDb, and YouTube.

**Response:**
```json
{
  "status": "success",
  "message": "Sync completed successfully"
}
```

If API keys are missing:
```json
{
  "status": "error",
  "message": "API keys (TMDB_API_KEY, YOUTUBE_API_KEY) are not configured. Set them in .env file.",
  "code": 503
}
```

### GET /api/health
Health check endpoint.

## Scheduler

Daily sync runs at **6:00 AM** (configurable via `SYNC_HOUR` and `SYNC_MINUTE`).

## Database

SQLite database stored in `data/netflix.db`.

### Schema

```sql
CREATE TABLE titles (
  id INTEGER PRIMARY KEY,
  tmdb_id STRING UNIQUE,
  title STRING,
  year INTEGER,
  type STRING,  -- 'movie' or 'series'
  rating FLOAT,
  popularity_rank INTEGER,
  poster_url STRING,
  overview TEXT,
  trailer_url STRING,
  genres STRING,  -- JSON array
  position INTEGER,
  scraped_at DATETIME
)
```

## Development

### API Keys Setup

1. **TMDb**: Register at [themoviedb.org](https://www.themoviedb.org/) → Settings → API → Get your key
2. **YouTube**: 
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable "YouTube Data API v3"
   - Go to Credentials → Create API Key

## Notes

- Without API keys, the sync will warn and continue without data enrichment
- FlixPatrol scraper uses 1s delay between requests to be respectful
- Posters are fetched from TMDb (width: 500px)
- Trailers are embedded from YouTube
- Database initializes automatically on first run
