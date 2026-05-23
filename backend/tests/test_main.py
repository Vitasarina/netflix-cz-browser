import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, PropertyMock
from fastapi.testclient import TestClient

from app.main import app
from app.models import Title
from app.database import get_db
from app import config


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_title():
    title = MagicMock(spec=Title)
    title.id = 1
    title.tmdb_id = "123"
    title.title = "Test Movie"
    title.year = 2023
    title.type = "movie"
    title.rating = 8.5
    title.popularity_rank = 1
    title.poster_url = "http://example.com/poster.jpg"
    title.overview = "Test overview"
    title.trailer_url = "http://youtube.com/embed/123"
    title.genres = '["Action"]'
    title.position = 1
    title.scraped_at = datetime(2023, 1, 1, 12, 0, 0)
    return title


class TestTrendingEndpoints:
    def test_get_trending_empty(self, client):
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/api/trending")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json() == []

    def test_get_trending_with_data(self, client, mock_title):
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = [mock_title]

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/api/trending")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Movie"

    def test_get_trending_filter_movie(self, client, mock_title):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_title
        ]

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/api/trending?type=movie")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_trending_filter_series(self, client):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/api/trending?type=series")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json() == []

    def test_get_trending_invalid_type(self, client):
        mock_db = MagicMock()

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/api/trending?type=invalid")
        app.dependency_overrides.clear()

        assert response.status_code == 400
        assert "Invalid type" in response.json()["detail"]

    def test_get_trending_detail_found(self, client, mock_title):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_title

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/api/trending/1")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json()["title"] == "Test Movie"

    def test_get_trending_detail_not_found(self, client):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/api/trending/999")
        app.dependency_overrides.clear()

        assert response.status_code == 404
        assert "Title not found" in response.json()["detail"]


class TestSyncEndpoint:
    def test_manual_sync_no_api_keys(self, client):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=False,
        ):
            response = client.post("/api/sync")
            assert response.status_code == 200
            assert response.json()["status"] == "error"

    @patch("app.main.sync_trending_data", return_value=True)
    def test_manual_sync_success(self, mock_sync, client):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            response = client.post("/api/sync")
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    @patch("app.main.sync_trending_data", return_value=False)
    def test_manual_sync_failure(self, mock_sync, client):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            response = client.post("/api/sync")
            assert response.status_code == 200
            assert response.json()["status"] == "error"


class TestHealthEndpoint:
    def test_health_check_success(self, client):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=True,
        ):
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["api_keys_configured"] is True
            assert "timestamp" in data

    def test_health_check_no_keys(self, client):
        with patch.object(
            type(config.settings),
            "api_keys_available",
            new_callable=PropertyMock,
            return_value=False,
        ):
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["api_keys_configured"] is False
