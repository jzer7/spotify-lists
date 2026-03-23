import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
load_dotenv()

SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative",
]


def get_auth_manager() -> SpotifyOAuth:
    """
    Creates and returns a SpotifyOAuth manager instance.
    Requires SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI env vars.
    """
    return SpotifyOAuth(scope=" ".join(SCOPES), open_browser=True)


def get_spotify_client() -> spotipy.Spotify:
    """
    Returns an authenticated Spotify client.
    """
    auth_manager = get_auth_manager()
    return spotipy.Spotify(auth_manager=auth_manager)
