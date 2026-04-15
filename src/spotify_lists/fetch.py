import spotipy

from .models import Playlist, Track


def get_all_playlists_metadata(sp: spotipy.Spotify) -> list[dict]:
    """
    Fetches metadata for all user playlists.
    Returns a list of dicts with 'id', 'name', 'tracks_total'.
    """
    playlists = []
    results = sp.current_user_playlists(limit=50)
    while results:
        for item in results["items"]:
            playlists.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "tracks_total": item["tracks"]["total"],
                    "public": item["public"],
                }
            )
        if results["next"]:
            results = sp.next(results)
        else:
            results = None
    return playlists


def get_playlist_tracks(sp: spotipy.Spotify, playlist_id: str) -> list[Track]:
    """
    Fetches all tracks for a given playlist.
    """
    tracks = []
    results = sp.playlist_items(playlist_id, additional_types=["track"])
    while results:
        for item in results["items"]:
            track = item.get("track")
            if track and track.get("id"):  # Ensure it's a track and not null
                # Handle local files or podcast episodes if any (api might return them)
                tracks.append(
                    Track(
                        name=track["name"],
                        artist=track["artists"][0]["name"] if track["artists"] else "Unknown",
                        uri=track["uri"],
                        album=track["album"]["name"] if track["album"] else None,
                    )
                )
        if results["next"]:
            results = sp.next(results)
        else:
            results = None
    return tracks


def get_full_playlist(sp: spotipy.Spotify, playlist_id: str) -> Playlist:
    """
    Fetches full playlist details including tracks.
    """
    pl_data = sp.playlist(playlist_id)
    tracks = get_playlist_tracks(sp, playlist_id)

    return Playlist(
        id=pl_data["id"],
        name=pl_data["name"],
        description=pl_data["description"] or "",
        public=pl_data["public"],
        collaborative=pl_data["collaborative"],
        owner_id=pl_data["owner"]["id"],
        tracks=tracks,
    )
