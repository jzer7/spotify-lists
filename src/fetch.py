import spotipy


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
