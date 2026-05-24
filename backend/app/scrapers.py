import logging
import json
import requests
from typing import Optional, Dict, List, Any, cast

logger = logging.getLogger(__name__)


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
                return cast(Dict[str, Any], data["results"][0])
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
            return cast(Dict[str, Any], response.json())
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error getting TMDb details for ID {tmdb_id}: {e}")
            return None

    def get_trending(self, media_type: str) -> List[Dict[str, Any]]:
        """Get trending titles from TMDB Discover API filtered by Netflix CZ watch provider"""
        if not self.api_key:
            logger.warning("TMDb API key not configured")
            return []

        try:
            url = f"{self.BASE_URL}discover/{media_type}"
            params = {
                "api_key": self.api_key,
                "with_watch_providers": "8",
                "watch_region": "CZ",
                "sort_by": "popularity.desc",
                "language": "en-US",
                "page": "1"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])
            titles: List[Dict[str, Any]] = []

            for position, result in enumerate(results[:10], 1):
                title_key = "title" if media_type == "movie" else "name"
                date_key = "release_date" if media_type == "movie" else "first_air_date"

                title_data: Dict[str, Any] = {
                    "title": result.get(title_key, ""),
                    "tmdb_id": result.get("id"),
                    "rating": result.get("vote_average"),
                    "overview": result.get("overview"),
                    "position": position,
                }

                poster_path = result.get("poster_path")
                if poster_path:
                    title_data["poster_url"] = f"{self.POSTER_URL}{poster_path}"

                date_str = result.get(date_key)
                if date_str:
                    title_data["year"] = int(date_str[:4])

                titles.append(title_data)

            return titles
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.error(f"Error fetching trending from TMDB Discover API: {e}")
            return []

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
            params: Dict[str, str | int] = {
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
