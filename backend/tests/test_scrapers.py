from unittest.mock import patch, MagicMock
import requests

from app.scrapers import TMDbAPI, YouTubeAPI


class TestTMDbAPI:
    def test_init(self):
        api = TMDbAPI("test_key")
        assert api.api_key == "test_key"

    @patch("app.scrapers.requests.get")
    def test_get_trending_movies_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 123,
                    "title": "Movie 1",
                    "poster_path": "/path1.jpg",
                    "vote_average": 8.5,
                    "overview": "Overview 1",
                    "release_date": "2023-01-01"
                },
                {
                    "id": 124,
                    "title": "Movie 2",
                    "poster_path": "/path2.jpg",
                    "vote_average": 7.5,
                    "overview": "Overview 2",
                    "release_date": "2023-02-01"
                }
            ]
        }
        mock_get.return_value = mock_response

        api = TMDbAPI("test_key")
        result = api.get_trending("movie")

        assert len(result) == 2
        assert result[0]["title"] == "Movie 1"
        assert result[0]["position"] == 1
        assert result[0]["rating"] == 8.5
        assert result[0]["year"] == 2023
        assert result[0]["poster_url"] == "https://image.tmdb.org/t/p/w500/path1.jpg"
        assert result[1]["position"] == 2

    @patch("app.scrapers.requests.get")
    def test_get_trending_series_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 456,
                    "name": "Series 1",
                    "poster_path": "/series1.jpg",
                    "vote_average": 8.0,
                    "overview": "Series overview",
                    "first_air_date": "2023-01-15"
                }
            ]
        }
        mock_get.return_value = mock_response

        api = TMDbAPI("test_key")
        result = api.get_trending("tv")

        assert len(result) == 1
        assert result[0]["title"] == "Series 1"
        assert result[0]["position"] == 1
        assert result[0]["rating"] == 8.0
        assert result[0]["year"] == 2023

    def test_get_trending_no_api_key(self):
        api = TMDbAPI("")
        result = api.get_trending("movie")
        assert result == []

    @patch("app.scrapers.requests.get")
    def test_get_trending_empty_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        api = TMDbAPI("test_key")
        result = api.get_trending("movie")
        assert result == []

    @patch("app.scrapers.requests.get")
    def test_get_trending_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("API error")

        api = TMDbAPI("test_key")
        result = api.get_trending("movie")
        assert result == []

    @patch("app.scrapers.requests.get")
    def test_get_trending_without_optional_fields(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 789,
                    "title": "Movie Without Details",
                }
            ]
        }
        mock_get.return_value = mock_response

        api = TMDbAPI("test_key")
        result = api.get_trending("movie")

        assert len(result) == 1
        assert result[0]["title"] == "Movie Without Details"
        assert result[0]["rating"] is None
        assert "year" not in result[0]
        assert "poster_url" not in result[0]

    @patch("app.scrapers.requests.get")
    def test_search_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"id": 123, "title": "Movie Title"}]
        }
        mock_get.return_value = mock_response

        api = TMDbAPI("test_key")
        result = api.search("Movie Title", "movie")

        assert result == {"id": 123, "title": "Movie Title"}

    def test_search_no_api_key(self):
        api = TMDbAPI("")
        result = api.search("Movie Title")
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_search_no_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        api = TMDbAPI("test_key")
        result = api.search("Nonexistent")
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_search_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("API down")

        api = TMDbAPI("test_key")
        result = api.search("Movie Title")
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_get_details_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 123,
            "title": "Movie",
            "vote_average": 8.5,
            "overview": "Overview",
            "poster_path": "/path.jpg",
            "genres": [{"name": "Action"}],
            "release_date": "2023-01-01"
        }
        mock_get.return_value = mock_response

        api = TMDbAPI("test_key")
        result = api.get_details(123, "movie")

        assert result["id"] == 123
        assert result["title"] == "Movie"

    def test_get_details_no_api_key(self):
        api = TMDbAPI("")
        result = api.get_details(123)
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_get_details_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("API error")

        api = TMDbAPI("test_key")
        result = api.get_details(123)
        assert result is None

    @patch.object(TMDbAPI, "search")
    @patch.object(TMDbAPI, "get_details")
    def test_enrich_title_success(self, mock_details, mock_search):
        mock_search.return_value = {"id": 123}
        mock_details.return_value = {
            "vote_average": 8.5,
            "overview": "Overview",
            "poster_path": "/path.jpg",
            "genres": [{"name": "Action"}],
            "release_date": "2023-01-01"
        }

        api = TMDbAPI("test_key")
        result = api.enrich_title("Movie", None, "movie")

        assert result["title"] == "Movie"
        assert result["rating"] == 8.5
        assert result["year"] == 2023

    @patch.object(TMDbAPI, "search")
    def test_enrich_title_no_search_result(self, mock_search):
        mock_search.return_value = None

        api = TMDbAPI("test_key")
        result = api.enrich_title("Nonexistent", None, "movie")

        assert result["title"] == "Nonexistent"
        assert result["tmdb_id"] is None


class TestYouTubeAPI:
    def test_init(self):
        api = YouTubeAPI("test_key")
        assert api.api_key == "test_key"

    @patch("app.scrapers.requests.get")
    def test_search_trailer_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [{"id": {"videoId": "dQw4w9WgXcQ"}}]
        }
        mock_get.return_value = mock_response

        api = YouTubeAPI("test_key")
        result = api.search_trailer("Movie", 2023)

        assert result == "https://www.youtube.com/embed/dQw4w9WgXcQ"

    def test_search_trailer_no_api_key(self):
        api = YouTubeAPI("")
        result = api.search_trailer("Movie", None)
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_search_trailer_no_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        api = YouTubeAPI("test_key")
        result = api.search_trailer("Nonexistent", None)
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_search_trailer_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("API error")

        api = YouTubeAPI("test_key")
        result = api.search_trailer("Movie", None)
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_search_trailer_missing_video_id(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": [{"id": {}}]}
        mock_get.return_value = mock_response

        api = YouTubeAPI("test_key")
        result = api.search_trailer("Movie", None)
        assert result is None

    @patch("app.scrapers.requests.get")
    def test_search_trailer_without_year(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [{"id": {"videoId": "abc123"}}]
        }
        mock_get.return_value = mock_response

        api = YouTubeAPI("test_key")
        result = api.search_trailer("Movie", None)

        assert result == "https://www.youtube.com/embed/abc123"
