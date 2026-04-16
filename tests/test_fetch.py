"""Unit tests for fetch.py."""

from typing import Any

from pytest_mock import MockerFixture

from spotify_lists.fetch import _tracks_page_to_tracks_list

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------


def _make_track_item(track_id: str, name: str) -> dict[str, Any]:
    return {
        "track": {
            "id": track_id,
            "name": name,
            "uri": f"spotify:track:{track_id}",
            "artists": [{"name": "Some Artist"}],
            "album": {"name": "Some Album"},
        }
    }


def _make_page(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": items}


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
        result = _tracks_page_to_tracks_list(sp, _make_page([_make_track_item("id-1", "Song A")]))
        assert len(result) == 1
        assert result[0].id == "id-1"
        assert result[0].name == "Song A"

    def test_single_page_multiple_tracks(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = _make_page([_make_track_item("id-1", "Song A"), _make_track_item("id-2", "Song B")])
        result = _tracks_page_to_tracks_list(sp, page)
        assert [t.id for t in result] == ["id-1", "id-2"]

    def test_multiple_pages_are_iterated(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        page1 = _make_page([_make_track_item("id-1", "Song A")])
        page2 = _make_page([_make_track_item("id-2", "Song B")])
        sp.next.side_effect = [page2, None]
        result = _tracks_page_to_tracks_list(sp, page1)
        assert [t.id for t in result] == ["id-1", "id-2"]
        assert sp.next.call_count == 2

    def test_empty_items_list_returns_empty(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        assert _tracks_page_to_tracks_list(sp, _make_page([])) == []

    def test_malformed_page_missing_items_breaks_and_returns_empty(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        result = _tracks_page_to_tracks_list(sp, {"no_items_key": []})
        assert result == []
        sp.next.assert_not_called()

    def test_track_item_missing_track_key_is_skipped(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = _make_page([{"no_track_key": {}}, _make_track_item("id-1", "Song A")])
        result = _tracks_page_to_tracks_list(sp, page)
        assert len(result) == 1
        assert result[0].id == "id-1"

    def test_malformed_track_dict_is_skipped(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = _make_page(
            [
                {"track": {"id": "bad"}},  # missing required fields — _track_dict_to_track returns None
                _make_track_item("id-1", "Song A"),
            ]
        )
        result = _tracks_page_to_tracks_list(sp, page)
        assert len(result) == 1
        assert result[0].id == "id-1"

    def test_duplicate_track_appears_multiple_times(self, mocker: MockerFixture) -> None:
        sp = mocker.MagicMock()
        sp.next.return_value = None
        page = _make_page([_make_track_item("id-1", "Song A"), _make_track_item("id-1", "Song A")])
        result = _tracks_page_to_tracks_list(sp, page)
        assert len(result) == 2
