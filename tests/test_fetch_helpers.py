"""Unit tests for fetch.py — track and artist parsing helpers."""

from typing import Any

from pytest_mock import MockerFixture

from spotify_lists.fetch import (
    _artists_list_to_str,
    _kv_is_type,
    _playlist_dict_to_playlist,
    _track_dict_to_track,
    _tracks_page_to_tracks_list,
)
from spotify_lists.models import Playlist, Track

from .conftest import make_page, make_track_item

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
        assert _kv_is_type("not-a-dict", "name", str) is False

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
        assert _track_dict_to_track("not-a-dict") is None  # type: ignore[arg-type]  # type: ignore[ty:invalid-argument-type]
        assert _track_dict_to_track(88) is None  # type: ignore[arg-type]  # type: ignore[ty:invalid-argument-type]


# ----------------------------------------------------------
# _tracks_page_to_tracks_list
# ----------------------------------------------------------


class TestTrackPageToTracks:
    def test_none_page_returns_empty(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        assert _tracks_page_to_tracks_list(sp, None) == []

    def test_single_page_single_track(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        result = _tracks_page_to_tracks_list(sp, make_page([make_track_item("id-1", "Song A")]))
        assert len(result) == 1
        assert result[0].id == "id-1"
        assert result[0].name == "Song A"

    def test_single_page_multiple_tracks(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = make_page([make_track_item("id-1", "Song A"), make_track_item("id-2", "Song B")])
        result = _tracks_page_to_tracks_list(sp, page)
        assert [t.id for t in result] == ["id-1", "id-2"]

    def test_multiple_pages_are_iterated(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        page1 = make_page([make_track_item("id-1", "Song A")])
        page2 = make_page([make_track_item("id-2", "Song B")])
        sp.next.side_effect = [page2, None]
        result = _tracks_page_to_tracks_list(sp, page1)
        assert [t.id for t in result] == ["id-1", "id-2"]
        assert sp.next.call_count == 2

    def test_empty_items_list_returns_empty(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        assert _tracks_page_to_tracks_list(sp, make_page([])) == []

    def test_malformed_page_missing_items_breaks_and_returns_empty(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        result = _tracks_page_to_tracks_list(sp, {"no_items_key": []})
        assert result == []
        sp.next.assert_not_called()

    def test_track_item_missing_track_key_is_skipped(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = make_page([{"no_track_key": {}}, make_track_item("id-1", "Song A")])
        result = _tracks_page_to_tracks_list(sp, page)
        assert len(result) == 1
        assert result[0].id == "id-1"

    def test_malformed_track_dict_is_skipped(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = make_page(
            [
                {"track": {"id": "bad"}},  # missing required fields — _track_dict_to_track returns None
                make_track_item("id-1", "Song A"),
            ]
        )
        result = _tracks_page_to_tracks_list(sp, page)
        assert len(result) == 1
        assert result[0].id == "id-1"

    def test_duplicate_track_appears_multiple_times(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = make_page([make_track_item("id-1", "Song A"), make_track_item("id-1", "Song A")])
        result = _tracks_page_to_tracks_list(sp, page)
        assert len(result) == 2


# ----------------------------------------------------------
# _playlist_dict_to_playlist
# ----------------------------------------------------------


class TestPlaylistDictToPlaylist:
    def test_valid_playlist(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        pl = _playlist_dict_to_playlist(sp, valid_playlist_dict)
        assert isinstance(pl, Playlist)
        assert pl.id == "pl-id-1"
        assert pl.name == "Kind of Blue"
        assert pl.description == "A classic"
        assert pl.public is True
        assert pl.collaborative is False
        assert pl.owner_id == "owner-1"
        assert pl.tracks_total == 9
        assert pl.tracks == []

    def test_none_returns_none(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        assert _playlist_dict_to_playlist(sp, None) is None

    def test_missing_id_returns_none(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        del valid_playlist_dict["id"]
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_missing_name_returns_none(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        del valid_playlist_dict["name"]
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_missing_owner_returns_none(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        del valid_playlist_dict["owner"]
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_owner_without_id_returns_none(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        valid_playlist_dict["owner"] = {"display_name": "no id here"}
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_missing_tracks_returns_none(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        del valid_playlist_dict["tracks"]
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_tracks_without_total_returns_none(
        self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]
    ) -> None:
        sp = mocker.MagicMock()
        valid_playlist_dict["tracks"] = {"items": []}
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_missing_public_returns_none(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        del valid_playlist_dict["public"]
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_missing_collaborative_returns_none(
        self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]
    ) -> None:
        sp = mocker.MagicMock()
        del valid_playlist_dict["collaborative"]
        assert _playlist_dict_to_playlist(sp, valid_playlist_dict) is None

    def test_missing_description_defaults_to_empty_string(
        self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]
    ) -> None:
        sp = mocker.MagicMock()
        del valid_playlist_dict["description"]
        pl = _playlist_dict_to_playlist(sp, valid_playlist_dict)
        assert pl is not None
        assert pl.description == ""

    def test_get_tracks_false_does_not_fetch_tracks(
        self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]
    ) -> None:
        sp = mocker.MagicMock()
        pl = _playlist_dict_to_playlist(sp, valid_playlist_dict, get_tracks=False)
        assert pl is not None
        assert pl.tracks == []
        sp.next.assert_not_called()

    def test_get_tracks_true_fetches_tracks(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        valid_playlist_dict["tracks"] = {
            "total": 1,
            "items": [
                {
                    "track": {
                        "id": "t-1",
                        "name": "So What",
                        "uri": "spotify:track:t-1",
                        "artists": [{"name": "Miles Davis"}],
                        "album": {"name": "Kind of Blue"},
                    }
                }
            ],
        }
        sp.next.return_value = None
        pl = _playlist_dict_to_playlist(sp, valid_playlist_dict, get_tracks=True)
        assert pl is not None
        assert len(pl.tracks) == 1
        assert pl.tracks[0].id == "t-1"
