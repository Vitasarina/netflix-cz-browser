import logging
import time
import json
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FlixPatrolScraper:
    BASE_URL = "https://flixpatrol.com/top10/netflix/czech-republic/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    @staticmethod
    def scrape_movies() -> List[Dict[str, Any]]:
        """Scrape top 10 movies from FlixPatrol"""
        try:
            response = requests.get(FlixPatrolScraper.BASE_URL + "movies/", headers=FlixPatrolScraper.HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            titles: List[Dict[str, Any]] = []

            rows = soup.find_all("tr", class_="table-row-a")
            for position, row in enumerate(rows[:10], 1):
                try:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        title_link = row.find("a", class_="chart-title")
                        if title_link:
                            title = title_link.get_text(strip=True)
                            titles.append({
                                "title": title,
                                "type": "movie",
                                "position": position
                            })
                except (AttributeError, ValueError) as e:
                    logger.warning(f"Error parsing row: {e}")

            time.sleep(1)
            return titles
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error scraping FlixPatrol movies: {e}")
            return []

    @staticmethod
    def scrape_series() -> List[Dict[str, Any]]:
        """Scrape top 10 series from FlixPatrol"""
        try:
            response = requests.get(FlixPatrolScraper.BASE_URL + "tv-shows/", headers=FlixPatrolScraper.HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            titles: List[Dict[str, Any]] = []

            rows = soup.find_all("tr", class_="table-row-a")
            for position, row in enumerate(rows[:10], 1):
                try:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        title_link = row.find("a", class_="chart-title")
                        if title_link:
                            title = title_link.get_text(strip=True)
                            titles.append({
                                "title": title,
                                "type": "series",
                                "position": position
                            })
                except (AttributeError, ValueError) as e:
                    logger.warning(f"Error parsing row: {e}")

            time.sleep(1)
            return titles
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error scraping FlixPatrol series: {e}")
            return []


class TMDbAPI:
    BASE_URL = "https://api.themoviedb.org/3/"
    POSTER_URL = "https://image.tmdb.org/t/p/w500"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search(self, title: str, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        """Search for a title on TMDb"""
        if not self.api_key:
            logger.warning("TMDb API key not configured")
            return None

        try:
            url = f"{self.BASE_URL}search/{media_type}"
            params = {
                "api_key": self.api_key,
                "query": title,
                "language": "en-US"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("results"):
                return data["results"][0]
            return None
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error searching TMDb for '{title}': {e}")
            return None

    def get_details(self, tmdb_id: int, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        """Get detailed information about a title"""
        if not self.api_key:
            logger.warning("TMDb API key not configured")
            return None

        try:
            url = f"{self.BASE_URL}{media_type}/{tmdb_id}"
            params = {
                "api_key": self.api_key,
                "language": "en-US"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error getting TMDb details for ID {tmdb_id}: {e}")
            return None

    def enrich_title(self, title: str, year: Optional[int], media_type: str) -> Dict[str, Any]:
        """Enrich a title with TMDb data"""
        result: Dict[str, Any] = {
            "title": title,
            "year": year,
            "rating": None,
            "overview": None,
            "poster_url": None,
            "genres": None,
            "tmdb_id": None
        }

        search_result = self.search(title, media_type)
        if not search_result:
            return result

        result["tmdb_id"] = search_result.get("id")

        details = self.get_details(result["tmdb_id"], media_type)
        if details:
            result["rating"] = details.get("vote_average")
            result["overview"] = details.get("overview")
            poster_path = details.get("poster_path")
            if poster_path:
                result["poster_url"] = f"{self.POSTER_URL}{poster_path}"
            genres = details.get("genres", [])
            if genres:
                result["genres"] = json.dumps([g["name"] for g in genres])
            if "release_date" in details and details["release_date"]:
                result["year"] = int(details["release_date"][:4])
            elif "first_air_date" in details and details["first_air_date"]:
                result["year"] = int(details["first_air_date"][:4])

        return result


class YouTubeAPI:
    BASE_URL = "https://www.googleapis.com/youtube/v3/search"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search_trailer(self, title: str, year: Optional[int]) -> Optional[str]:
        """Search for a trailer on YouTube and return embed URL"""
        if not self.api_key:
            logger.warning("YouTube API key not configured")
            return None

        try:
            query = f"{title} {year} official trailer" if year else f"{title} official trailer"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 1,
                "key": self.api_key
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("items"):
                video_id = data["items"][0]["id"]["videoId"]
                return f"https://www.youtube.com/embed/{video_id}"
            return None
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.error(f"Error searching YouTube for '{title}': {e}")
            return None
