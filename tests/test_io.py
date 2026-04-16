"""Unit tests for io.py."""

from pathlib import Path

import pytest
import yaml

from spotify_lists.io import save_playlist
from spotify_lists.models import Playlist, Track

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def playlist() -> Playlist:
    return Playlist(
        id="pl-id-1",
        owner_id="owner-1",
        name="My Playlist",
        description="A test playlist",
        public=True,
        tracks=[
            Track(id="t-1", name="Song A", artists="Artist A", uri="spotify:track:t-1", album="Album A"),
        ],
    )


# ---------------------------------------------------------------------------
# save_playlist
# ---------------------------------------------------------------------------


class TestSavPlaylist:
    def test_creates_yaml_file(self, playlist: Playlist, tmp_path: Path) -> None:
        save_playlist(playlist, tmp_path)
        assert (tmp_path / "playlist_pl-id-1.yaml").exists()

    def test_creates_directory_if_missing(self, playlist: Playlist, tmp_path: Path) -> None:
        target = tmp_path / "nested" / "dir"
        save_playlist(playlist, target)
        assert (target / "playlist_pl-id-1.yaml").exists()

    def test_yaml_content_matches_playlist(self, playlist: Playlist, tmp_path: Path) -> None:
        save_playlist(playlist, tmp_path)
        with open(tmp_path / "playlist_pl-id-1.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["id"] == "pl-id-1"
        assert data["name"] == "My Playlist"
        assert data["description"] == "A test playlist"
        assert data["public"] is True
        assert data["owner_id"] == "owner-1"
        assert len(data["tracks"]) == 1
        assert data["tracks"][0]["name"] == "Song A"

    def test_overwrites_existing_file(self, playlist: Playlist, tmp_path: Path) -> None:
        save_playlist(playlist, tmp_path)
        playlist.description = "updated"
        save_playlist(playlist, tmp_path)
        with open(tmp_path / "playlist_pl-id-1.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["description"] == "updated"

    def test_playlist_with_no_tracks(self, tmp_path: Path) -> None:
        playlist = Playlist(id="pl-empty", owner_id="o-1", name="Empty")
        save_playlist(playlist, tmp_path)
        with open(tmp_path / "playlist_pl-empty.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["tracks"] == []

    def test_unicode_name_preserved_in_content(self, tmp_path: Path) -> None:
        # Non-ASCII letters pass isalpha(), so the full name is kept in the filename
        playlist = Playlist(id="pl-unicode", owner_id="o-1", name="Café")
        save_playlist(playlist, tmp_path)
        with open(tmp_path / "playlist_pl-unicode.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["name"] == "Café"
