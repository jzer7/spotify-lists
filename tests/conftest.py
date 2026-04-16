"""Shared pytest fixtures and helpers for fetch tests."""

from typing import Any

import pytest


@pytest.fixture()
def valid_artists() -> list[dict[str, Any]]:
    return [{"name": "Miles Davis"}, {"name": "Bill Evans"}]


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
def valid_playlist_dict() -> dict[str, Any]:
    return {
        "id": "pl-id-1",
        "name": "Kind of Blue",
        "description": "A classic",
        "public": True,
        "collaborative": False,
        "owner": {"id": "owner-1"},
        "tracks": {"total": 9, "items": []},
    }


# ---------------------------------------------------------------------------
# Track / page builder helpers (used across multiple test modules)
# ---------------------------------------------------------------------------


def make_track_item(track_id: str, name: str) -> dict[str, Any]:
    return {
        "track": {
            "id": track_id,
            "name": name,
            "uri": f"spotify:track:{track_id}",
            "artists": [{"name": "Some Artist"}],
            "album": {"name": "Some Album"},
        }
    }


def make_playlist_item(playlist_id: str, name: str) -> dict[str, Any]:
    return {
        "id": playlist_id,
        "name": name,
        "description": "",
        "public": False,
        "collaborative": False,
        "owner": {"id": "owner-1"},
        "tracks": {"total": 0, "items": []},
    }


def make_page(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": items}
