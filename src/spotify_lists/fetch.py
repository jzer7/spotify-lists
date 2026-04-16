import logging
from typing import Any

from spotipy import Spotify
from spotipy.exceptions import SpotifyException

from .models import Playlist, Track

logger = logging.getLogger(__name__)

# When retrieving collections, Spotify API paginates results.
# The template for a "page" looks like:
# {
#     href:     <url_to_api_endpoint>
#     limit:    <max_number_of_elements_per_page>
#     offset:   <index_of_first_element_in_page>
#     next:     <url_to_next_page> or None
#     previous: <url_to_previous_page> or None
#     total:    <total_number_of_elements>
#     items:    [...]
# }
# The elements inside `items` are the actual playlists or tracks, their format and meaning depends on the endpoint.


def _kv_is_type(
    obj: Any,
    field_name: str,
    expected_type: type,
) -> bool:
    """Checks if `obj` is a dictionary containing `field_name` of type `expected_type`."""
    if obj is None or not isinstance(obj, dict):
        return False
    if field_name not in obj or not isinstance(obj[field_name], expected_type):
        return False
    return True


def _playlist_dict_to_playlist(
    sp: Spotify,
    pl_dict: dict[str, Any] | None,
    get_tracks: bool = False,
) -> Playlist | None:
    """Converts a Spotify playlist dictionary to a Playlist object.

    If `get_tracks` is True, it will also fetch the tracks for the playlist.
    """

    if (
        pl_dict is None
        or not isinstance(pl_dict, dict)
        or not _kv_is_type(pl_dict, "id", str)
        or not _kv_is_type(pl_dict, "name", str)
        or not _kv_is_type(pl_dict, "owner", dict)
        or not _kv_is_type(pl_dict, "tracks", dict)
        or not _kv_is_type(pl_dict, "public", bool)
        or not _kv_is_type(pl_dict, "collaborative", bool)
    ):
        logger.warning(f"Skipping malformed playlist item: {pl_dict}")
        return None

    owner_dict = pl_dict["owner"]
    if not _kv_is_type(owner_dict, "id", str):
        logger.warning(f"Skipping playlist with invalid owner structure: {owner_dict}")
        return None

    tracks_page = pl_dict["tracks"]
    if not _kv_is_type(tracks_page, "total", int):
        logger.warning(f"Skipping playlist with invalid tracks page: {tracks_page}")
        return None

    pl = Playlist(
        id=pl_dict["id"],
        owner_id=owner_dict["id"],
        name=pl_dict["name"],
        description=pl_dict.get("description", ""),
        public=pl_dict.get("public", False),
        collaborative=pl_dict.get("collaborative", False),
        tracks_total=tracks_page["total"],
        tracks=[],
    )

    if get_tracks:
        tracks = _tracks_page_to_tracks_list(sp, tracks_page)
        pl.tracks = tracks

    return pl


def _artists_list_to_str(artists: list[dict[str, Any]]) -> str:
    """Converts a list of artist dictionaries to a comma-separated string of artist names."""
    if not artists or not isinstance(artists, list):
        return ""
    artist_names = [artist["name"].strip() for artist in artists if _kv_is_type(artist, "name", str)]
    return ";".join(artist_names)


def _track_dict_to_track(tr_dict: dict[str, Any] | None) -> Track | None:
    """Converts a Spotify track dictionary to a Track object."""

    if (
        not tr_dict
        or not isinstance(tr_dict, dict)
        or not _kv_is_type(tr_dict, "id", str)
        or not _kv_is_type(tr_dict, "name", str)
        or not _kv_is_type(tr_dict, "artists", list)
        or not _kv_is_type(tr_dict, "album", dict)
        or not _kv_is_type(tr_dict, "uri", str)
    ):
        logger.warning(f"Skipping malformed track info: {tr_dict}")
        return None

    artists_dict = tr_dict["artists"]
    if not artists_dict or not isinstance(artists_dict, list):
        logger.warning(f"Skipping track with invalid artists structure: {artists_dict}")
        return None

    album_dict = tr_dict["album"]
    if not album_dict or not isinstance(album_dict, dict) or not _kv_is_type(album_dict, "name", str):
        logger.warning(f"Skipping track with invalid album structure: {album_dict}")
        return None

    track = Track(
        id=tr_dict["id"],
        name=tr_dict["name"],
        artists=_artists_list_to_str(artists_dict),
        album=album_dict["name"],
        uri=tr_dict["uri"],
    )
    return track


def _tracks_page_to_tracks_list(
    sp: Spotify,
    page: dict[str, Any] | None,
) -> list[Track]:
    tracks: list[Track] = []

    while page:
        if not _kv_is_type(page, "items", list):
            logger.warning(f"Skipping malformed playlist items page: {page}")
            break
        # A track can appear multiple times in a playlist.
        # Each occurrence is a separate item in the `items` list.
        for tr_dict in page["items"]:
            # tr_dict is an occurrence of a track. It contains the actual
            # track info inside a "track" field.
            if not _kv_is_type(tr_dict, "track", dict):
                logger.warning(f"Skipping malformed track item: {tr_dict}")
                continue

            track = _track_dict_to_track(tr_dict["track"])
            if track:
                tracks.append(track)

        page = sp.next(page)

    return tracks


def get_all_playlists(
    sp: Spotify,
    get_tracks: bool = False,
) -> list[Playlist]:
    """
    Fetches all playlists the current user has access to.

    If `get_tracks` is True, it will also fetch the tracks for each playlist.

    Returns:
      list of Playlist objects
    """
    playlists = []

    page = sp.current_user_playlists(limit=50)
    while page:
        if not _kv_is_type(page, "items", list):
            logger.warning(f"Skipping malformed playlists page: {page}")
            break
        for pl_dict in page["items"]:
            playlist = _playlist_dict_to_playlist(sp, pl_dict, get_tracks=get_tracks)
            if playlist:
                playlists.append(playlist)

        page = sp.next(page)

    return playlists


def get_one_playlist(
    sp: Spotify,
    playlist_id: str,
    get_tracks: bool = True,
) -> Playlist:
    """
    Fetches a single playlist.

    If `get_tracks` is True, it will also fetch the tracks for the playlist.

    Returns:
      Playlist object
    """
    try:
        pl_dict = sp.playlist(playlist_id)
    except SpotifyException as e:
        logger.error(f"Spotify API error fetching playlist {playlist_id}: {e}")
        raise ValueError(f"Failed to retrieve playlist data for ID {playlist_id}") from e
    except Exception as e:
        logger.error(f"Error fetching playlist {playlist_id}: {e}")
        raise ValueError(f"Failed to retrieve playlist data for ID {playlist_id}") from e

    playlist = _playlist_dict_to_playlist(sp, pl_dict, get_tracks=get_tracks)

    if not playlist:
        raise ValueError(f"Failed to retrieve playlist data for ID {playlist_id}")
    return playlist
