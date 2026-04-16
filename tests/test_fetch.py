"""Unit tests for fetch.py — public API: get_all_playlists, get_one_playlist."""

from typing import Any

import pytest
from pytest_mock import MockerFixture
from spotipy.exceptions import SpotifyException

from spotify_lists.fetch import get_all_playlists, get_one_playlist
from spotify_lists.models import Playlist

from .conftest import make_page, make_playlist_item

# ----------------------------------------------------------
# get_all_playlists
# ----------------------------------------------------------


class TestGetAllPlaylists:
    def test_returns_empty_list_when_no_playlists(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.current_user_playlists.return_value = make_page([])
        sp.next.return_value = None
        assert get_all_playlists(sp) == []

    def test_returns_playlists_from_single_page(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.current_user_playlists.return_value = make_page(
            [make_playlist_item("pl-1", "Playlist One"), make_playlist_item("pl-2", "Playlist Two")]
        )
        sp.next.return_value = None
        result = get_all_playlists(sp)
        assert len(result) == 2
        assert [pl.id for pl in result] == ["pl-1", "pl-2"]

    def test_paginates_across_multiple_pages(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        page1 = make_page([make_playlist_item("pl-1", "Playlist One")])
        page2 = make_page([make_playlist_item("pl-2", "Playlist Two")])
        sp.current_user_playlists.return_value = page1
        sp.next.side_effect = [page2, None]
        result = get_all_playlists(sp)
        assert [pl.id for pl in result] == ["pl-1", "pl-2"]
        assert sp.next.call_count == 2

    def test_skips_malformed_playlist_items(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.current_user_playlists.return_value = make_page(
            [
                {"id": "bad"},  # missing required fields
                make_playlist_item("pl-1", "Good Playlist"),
            ]
        )
        sp.next.return_value = None
        result = get_all_playlists(sp)
        assert len(result) == 1
        assert result[0].id == "pl-1"

    def test_breaks_on_malformed_page(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.current_user_playlists.return_value = {"no_items_key": []}
        result = get_all_playlists(sp)
        assert result == []
        sp.next.assert_not_called()

    def test_passes_get_tracks_to_playlist_converter(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.current_user_playlists.return_value = make_page([make_playlist_item("pl-1", "Playlist One")])
        sp.next.return_value = None
        result = get_all_playlists(sp, get_tracks=False)
        assert len(result) == 1
        assert result[0].tracks == []


# ----------------------------------------------------------
# get_one_playlist
# ----------------------------------------------------------


class TestGetOnePlaylist:
    def test_returns_playlist(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
        sp = mocker.MagicMock()
        sp.playlist.return_value = valid_playlist_dict
        sp.next.return_value = None
        pl = get_one_playlist(sp, "pl-id-1")
        assert isinstance(pl, Playlist)
        assert pl.id == "pl-id-1"
        sp.playlist.assert_called_once_with("pl-id-1")

    def test_raises_on_spotify_exception(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.playlist.side_effect = SpotifyException(404, -1, "not found")
        with pytest.raises(ValueError, match="pl-id-1"):
            get_one_playlist(sp, "pl-id-1")

    def test_raises_on_generic_exception(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.playlist.side_effect = RuntimeError("network error")
        with pytest.raises(ValueError, match="pl-id-1"):
            get_one_playlist(sp, "pl-id-1")

    def test_raises_when_api_returns_none(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.playlist.return_value = None
        with pytest.raises(ValueError, match="pl-id-1"):
            get_one_playlist(sp, "pl-id-1")

    def test_raises_when_api_returns_malformed_dict(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.playlist.return_value = {"id": "incomplete"}
        with pytest.raises(ValueError, match="pl-id-1"):
            get_one_playlist(sp, "pl-id-1")

    def test_get_tracks_true_fetches_tracks(self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]) -> None:
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
        sp = mocker.MagicMock()
        sp.playlist.return_value = valid_playlist_dict
        sp.next.return_value = None
        pl = get_one_playlist(sp, "pl-id-1", get_tracks=True)
        assert len(pl.tracks) == 1
        assert pl.tracks[0].id == "t-1"

    def test_get_tracks_false_returns_empty_tracks(
        self, mocker: MockerFixture, valid_playlist_dict: dict[str, Any]
    ) -> None:
        sp = mocker.MagicMock()
        sp.playlist.return_value = valid_playlist_dict
        pl = get_one_playlist(sp, "pl-id-1", get_tracks=False)
        assert pl.tracks == []
        sp.next.assert_not_called()
