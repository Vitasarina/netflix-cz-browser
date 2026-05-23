from unittest.mock import patch, MagicMock, PropertyMock

from app.database import init_db, get_db, sync_trending_data
from app import config


class TestInitDB:
    def test_init_db_creates_directory(self):
        with patch("app.database.os.makedirs") as mock_mkdir:
            with patch("app.database.Base.metadata.create_all"):
                init_db()
                mock_mkdir.assert_called_once_with("data", exist_ok=True)

    def test_init_db_creates_all_tables(self):
        with patch("app.database.os.makedirs"):
            with patch("app.database.Base.metadata.create_all") as mock_create:
                init_db()
                mock_create.assert_called_once()


class TestGetDB:
    def test_get_db_yields_session(self):
        mock_session = MagicMock()
        with patch("app.database.SessionLocal", return_value=mock_session):
            gen = get_db()
            session = next(gen)
            assert session == mock_session

            try:
                next(gen)
            except StopIteration:
                pass

            mock_session.close.assert_called_once()

    def test_get_db_closes_on_exception(self):
        mock_session = MagicMock()
        with patch("app.database.SessionLocal", return_value=mock_session):
            gen = get_db()
            next(gen)

            try:
                gen.throw(Exception("Test"))
            except Exception:
                pass

            mock_session.close.assert_called_once()


class TestSyncTrendingData:
    def test_sync_returns_false_no_keys(self):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=False,
        ):
            result = sync_trending_data()
            assert result is False

    @patch("app.database.SessionLocal")
    @patch("app.database.YouTubeAPI")
    @patch("app.database.TMDbAPI")
    @patch("app.database.FlixPatrolScraper.scrape_series", return_value=[])
    @patch("app.database.FlixPatrolScraper.scrape_movies", return_value=[])
    def test_sync_success_with_empty_results(
        self, mock_movies, mock_series, mock_tmdb, mock_yt, mock_session_local
    ):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            result = sync_trending_data()
            assert result is True
            mock_db.commit.assert_called()
            mock_db.close.assert_called()

    @patch("app.database.SessionLocal")
    @patch("app.database.YouTubeAPI")
    @patch("app.database.TMDbAPI")
    @patch("app.database.FlixPatrolScraper.scrape_series", return_value=[])
    @patch("app.database.FlixPatrolScraper.scrape_movies")
    def test_sync_with_movies(
        self, mock_movies, mock_series, mock_tmdb, mock_yt, mock_session_local
    ):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_movies.return_value = [{"title": "Test", "position": 1}]

            mock_tmdb_inst = MagicMock()
            mock_tmdb_inst.enrich_title.return_value = {
                "title": "Test", "tmdb_id": 1, "year": 2023, "rating": 8.5,
                "overview": "Test", "poster_url": None, "genres": None, "position": 1
            }
            mock_tmdb.return_value = mock_tmdb_inst

            mock_yt_inst = MagicMock()
            mock_yt_inst.search_trailer.return_value = None
            mock_yt.return_value = mock_yt_inst

            result = sync_trending_data()
            assert result is True
            assert mock_db.add.called
            mock_db.commit.assert_called()

    @patch("app.database.SessionLocal")
    @patch("app.database.YouTubeAPI")
    @patch("app.database.TMDbAPI")
    @patch("app.database.FlixPatrolScraper.scrape_series")
    @patch("app.database.FlixPatrolScraper.scrape_movies")
    def test_sync_handles_request_exception(
        self, mock_movies, mock_series, mock_tmdb, mock_yt, mock_session_local
    ):
        import requests

        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_movies.side_effect = requests.RequestException("Network error")

            result = sync_trending_data()
            assert result is False
            mock_db.rollback.assert_called()
            mock_db.close.assert_called()

    @patch("app.database.SessionLocal")
    @patch("app.database.YouTubeAPI")
    @patch("app.database.TMDbAPI")
    @patch("app.database.FlixPatrolScraper.scrape_series")
    @patch("app.database.FlixPatrolScraper.scrape_movies")
    def test_sync_handles_value_error(
        self, mock_movies, mock_series, mock_tmdb, mock_yt, mock_session_local
    ):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_movies.side_effect = ValueError("Invalid data")

            result = sync_trending_data()
            assert result is False
            mock_db.rollback.assert_called()

    @patch("app.database.SessionLocal")
    @patch("app.database.YouTubeAPI")
    @patch("app.database.TMDbAPI")
    @patch("app.database.FlixPatrolScraper.scrape_series")
    @patch("app.database.FlixPatrolScraper.scrape_movies")
    def test_sync_handles_sqlalchemy_error(
        self, mock_movies, mock_series, mock_tmdb, mock_yt, mock_session_local
    ):
        from sqlalchemy.exc import SQLAlchemyError

        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            mock_db = MagicMock()
            mock_db.commit.side_effect = SQLAlchemyError("DB error")
            mock_session_local.return_value = mock_db
            mock_movies.return_value = [{"title": "Test", "position": 1}]

            mock_tmdb_inst = MagicMock()
            mock_tmdb_inst.enrich_title.return_value = {
                "title": "Test", "tmdb_id": 1, "year": 2023, "rating": 8.5,
                "overview": "Test", "poster_url": None, "genres": None, "position": 1
            }
            mock_tmdb.return_value = mock_tmdb_inst

            mock_yt_inst = MagicMock()
            mock_yt_inst.search_trailer.return_value = None
            mock_yt.return_value = mock_yt_inst

            result = sync_trending_data()
            assert result is False
            mock_db.rollback.assert_called()

    @patch("app.database.SessionLocal")
    @patch("app.database.YouTubeAPI")
    @patch("app.database.TMDbAPI")
    @patch("app.database.FlixPatrolScraper.scrape_series")
    @patch("app.database.FlixPatrolScraper.scrape_movies")
    def test_sync_with_series(
        self, mock_movies, mock_series, mock_tmdb, mock_yt, mock_session_local
    ):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_movies.return_value = []
            mock_series.return_value = [{"title": "Test Series", "position": 1}]

            mock_tmdb_inst = MagicMock()
            mock_tmdb_inst.enrich_title.return_value = {
                "title": "Test Series", "tmdb_id": 2, "year": 2023, "rating": 8.0,
                "overview": "Test", "poster_url": "http://url", "genres": "[]", "position": 1
            }
            mock_tmdb.return_value = mock_tmdb_inst

            mock_yt_inst = MagicMock()
            mock_yt_inst.search_trailer.return_value = "http://youtube.com/embed/123"
            mock_yt.return_value = mock_yt_inst

            result = sync_trending_data()
            assert result is True
            mock_db.commit.assert_called()
