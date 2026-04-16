"""Unit tests for fetch.py — track and artist parsing helpers."""

from typing import Any

import pytest

from spotify_lists.fetch import _artists_list_to_str, _kv_is_type, _track_dict_to_track
from spotify_lists.models import Track

# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------


@pytest.fixture()
def valid_track_dict() -> dict[str, Any]:
    return {
        "id": "track-id-1",
        "name": "Blue in Green",
        "uri": "spotify:track:track-id-1",
        "artists": [{"name": "Miles Davis"}],
        "album": {"name": "Kind of Blue"},
    }


@pytest.fixture()
def valid_artists() -> list[dict[str, Any]]:
    return [{"name": "Miles Davis"}, {"name": "Bill Evans"}]


# ----------------------------------------------------------
# _kv_is_type
# ----------------------------------------------------------


class TestKvIsType:
    # ------------------------------------------------------
    # Valid object

    def test_valid_key_and_type(self) -> None:
        d = {"name": "Miles Davis"}
        assert _kv_is_type(d, "name", str) is True

    # ------------------------------------------------------
    # Invalid object

    def test_null_value(self) -> None:
        d = {"name": None}
        assert _kv_is_type(d, "name", str) is False

    def test_non_dict_input(self) -> None:
        assert _kv_is_type("not-a-dict", "name", str) is False  # type: ignore[arg-type]

    def test_missing_key(self) -> None:
        d = {"id": "123"}
        assert _kv_is_type(d, "name", str) is False

    def test_wrong_type(self) -> None:
        d = {"name": 42}
        assert _kv_is_type(d, "name", str) is False


# ----------------------------------------------------------
# _artists_list_to_str
# ----------------------------------------------------------


class TestArtistsListToStr:
    def test_single_artist(self) -> None:
        assert _artists_list_to_str([{"name": "Miles Davis"}]) == "Miles Davis"

    def test_multiple_artists(self, valid_artists: list[dict[str, Any]]) -> None:
        assert _artists_list_to_str(valid_artists) == "Miles Davis;Bill Evans"

    def test_strips_whitespace(self) -> None:
        assert _artists_list_to_str([{"name": "  Miles Davis  "}]) == "Miles Davis"

    def test_skips_artists_without_name_key(self) -> None:
        artists: list[dict[str, Any]] = [{"name": "Miles Davis"}, {"id": "no-name"}]
        assert _artists_list_to_str(artists) == "Miles Davis"

    def test_skips_artists_with_non_string_name(self) -> None:
        artists: list[dict[str, Any]] = [{"name": 42}, {"name": "Bill Evans"}]
        assert _artists_list_to_str(artists) == "Bill Evans"

    def test_empty_list_returns_empty_string(self) -> None:
        assert _artists_list_to_str([]) == ""

    def test_all_artists_invalid_returns_empty_string(self) -> None:
        artists: list[dict[str, Any]] = [{"id": "a"}, {"id": "b"}]
        assert _artists_list_to_str(artists) == ""


# ----------------------------------------------------------
# _track_dict_to_track
# ----------------------------------------------------------


class TestTrackDictToTrack:
    def test_valid_track(self, valid_track_dict: dict[str, Any]) -> None:
        track = _track_dict_to_track(valid_track_dict)
        assert isinstance(track, Track)
        assert track.id == "track-id-1"
        assert track.name == "Blue in Green"
        assert track.uri == "spotify:track:track-id-1"
        assert track.artists == "Miles Davis"
        assert track.album == "Kind of Blue"

    def test_multiple_artists_joined(self, valid_track_dict: dict[str, Any]) -> None:
        valid_track_dict["artists"] = [{"name": "Miles Davis"}, {"name": "Bill Evans"}]
        track = _track_dict_to_track(valid_track_dict)
        assert track is not None
        assert track.artists == "Miles Davis;Bill Evans"

    def test_none_returns_none(self) -> None:
        assert _track_dict_to_track(None) is None

    def test_missing_id_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        del valid_track_dict["id"]
        assert _track_dict_to_track(valid_track_dict) is None

    def test_missing_name_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        del valid_track_dict["name"]
        assert _track_dict_to_track(valid_track_dict) is None

    def test_missing_uri_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        del valid_track_dict["uri"]
        assert _track_dict_to_track(valid_track_dict) is None

    def test_missing_artists_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        del valid_track_dict["artists"]
        assert _track_dict_to_track(valid_track_dict) is None

    def test_artists_not_a_list_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        valid_track_dict["artists"] = "Miles Davis"
        assert _track_dict_to_track(valid_track_dict) is None

    def test_empty_artists_list_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        # Reaches the `if not artists_dict` guard after the initial type check passes
        valid_track_dict["artists"] = []
        assert _track_dict_to_track(valid_track_dict) is None

    def test_missing_album_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        del valid_track_dict["album"]
        assert _track_dict_to_track(valid_track_dict) is None

    def test_album_without_name_returns_none(self, valid_track_dict: dict[str, Any]) -> None:
        valid_track_dict["album"] = {"id": "no-name"}
        assert _track_dict_to_track(valid_track_dict) is None

    def test_non_dict_input_returns_none(self) -> None:
        assert _track_dict_to_track("not-a-dict") is None  # type: ignore[arg-type]
