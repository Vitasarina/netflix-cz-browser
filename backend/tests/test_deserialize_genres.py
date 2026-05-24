import pytest
from app.main import TitleResponse


class TestDeserializeGenres:
    """Unit tests for TitleResponse.deserialize_genres validator"""

    def test_none_input_returns_none(self):
        """Input is None → should return None"""
        result = TitleResponse.deserialize_genres(None)
        assert result is None

    def test_list_input_returns_as_is(self):
        """Input is already a list → return as-is"""
        genres = ["Action", "Drama", "Comedy"]
        result = TitleResponse.deserialize_genres(genres)
        assert result == genres
        assert result is genres

    def test_empty_list_returns_empty_list(self):
        """Input is an empty list → return empty list"""
        result = TitleResponse.deserialize_genres([])
        assert result == []

    def test_valid_json_string_deserializes(self):
        """Input is a valid JSON string → return deserialized list"""
        json_str = '["drama", "thriller"]'
        result = TitleResponse.deserialize_genres(json_str)
        assert result == ["drama", "thriller"]

    def test_valid_json_single_item(self):
        """Input is valid JSON with single item → return list with item"""
        json_str = '["Action"]'
        result = TitleResponse.deserialize_genres(json_str)
        assert result == ["Action"]

    def test_valid_json_empty_array(self):
        """Input is valid empty JSON array → return empty list"""
        json_str = '[]'
        result = TitleResponse.deserialize_genres(json_str)
        assert result == []

    def test_invalid_json_string_returns_none(self):
        """Input is an invalid JSON string → should not raise, return None"""
        invalid_json = '["Action", "Drama"'
        result = TitleResponse.deserialize_genres(invalid_json)
        assert result is None

    def test_malformed_json_returns_none(self):
        """Input is malformed JSON → should not raise, return None"""
        invalid_json = '{not valid json}'
        result = TitleResponse.deserialize_genres(invalid_json)
        assert result is None

    def test_empty_string_returns_none(self):
        """Input is empty string → should not raise, return None"""
        result = TitleResponse.deserialize_genres('')
        assert result is None

    def test_int_input_returns_none(self):
        """Input is an unexpected type (int) → should not raise, return None"""
        result = TitleResponse.deserialize_genres(123)
        assert result is None

    def test_dict_input_returns_none(self):
        """Input is an unexpected type (dict) → should not raise, return None"""
        result = TitleResponse.deserialize_genres({"genre": "Action"})
        assert result is None

    def test_float_input_returns_none(self):
        """Input is an unexpected type (float) → should not raise, return None"""
        result = TitleResponse.deserialize_genres(3.14)
        assert result is None

    def test_bool_input_returns_none(self):
        """Input is an unexpected type (bool) → should not raise, return None"""
        result = TitleResponse.deserialize_genres(True)
        assert result is None
