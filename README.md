# Netflix CZ Trending Browser

Lokální webová aplikace pro sledování Netflix trendů v České republice.
Běží na Tailscale mašině (`agent`, 100.117.196.90).

## Stack

| Služba | Technologie | Port |
|--------|-------------|------|
| `backend` | Python 3.12 / FastAPI | 8000 (interní) |
| `frontend` | Node 20 / React + Vite → nginx | 3000 (exposed) |
| `scheduler` | Python (stejný image jako backend) | — |

## Požadavky

- Docker & Docker Compose v2
- API klíče (viz níže)

## Rychlý start

```bash
# 1. Klonuj repo
git clone https://github.com/Vitasarina/netflix-cz-browser.git
cd netflix-cz-browser

# 2. Nastav env vars
cp .env.example .env
# Doplň TMDB_API_KEY a YOUTUBE_API_KEY do .env

# 3. Spusť stack
cd docker
docker compose up --build
```

Frontend bude dostupný na `http://localhost:3000` (nebo přes Tailscale `http://100.117.196.90:3000`).

## Environment Variables

| Proměnná | Popis | Povinná |
|----------|-------|--------|
| `TMDB_API_KEY` | API klíč pro The Movie Database | Ano (pro data) |
| `YOUTUBE_API_KEY` | API klíč pro YouTube Data API | Ano (pro trailery) |
| `DATABASE_URL` | SQLite connection string | Ne (má default) |

> **Poznámka:** Bez API klíčů stack nastartuje, ale backend bude vracet prázdná data.

## První synchronizace dat

Po spuštění stacku spusť první sync ručně:

```bash
docker compose -f docker/docker-compose.yml exec backend python -c "from scheduler import sync_now; sync_now()"
```

Scheduler pak běží automaticky každou hodinu.

## Adresářová struktura

```
netflix-cz-browser/
├── backend/          # FastAPI aplikace
│   ├── main.py
│   ├── scheduler.py
│   └── requirements.txt
├── frontend/         # React + Vite aplikace
│   ├── src/
│   ├── index.html
│   ├── vite.config.js
│   └── nginx.conf
├── docker/           # Docker konfigurace
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── data/             # SQLite data (gitignored)
├── .env.example
└── README.md
```

## Vývoj

Backend a frontend devs mohou pushovat do svých adresářů nezávisle.
Pro lokální vývoj bez Dockeru:

```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```
