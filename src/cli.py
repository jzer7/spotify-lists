import logging
from pathlib import Path

import click

from src.auth import get_spotify_client
from src.fetch import get_all_playlists_metadata, get_full_playlist
from src.io import save_playlist

logger = logging.getLogger("cli")
PLAYLISTS_DIR = Path("playlists")


@click.group()
def cli() -> None:
    """Spotify playlist utility."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@cli.command()
def login() -> None:
    """Authenticate with Spotify."""
    sp = get_spotify_client()
    user = sp.current_user()
    logger.info(f"Logged in as {user['display_name']} ({user['id']})")


@cli.command("list")
def list_playlists() -> None:
    """List all Spotify playlists."""
    sp = get_spotify_client()
    playlists = get_all_playlists_metadata(sp)

    for pl in playlists:
        logger.info(f"{pl['name']} (ID: {pl['id']}, Tracks: {pl['tracks_total']}, Public: {pl['public']})")


@cli.command()
@click.option("--id", help="Playlist ID to download")
def download(id: str) -> None:
    """Download playlists to local YAML files."""
    sp = get_spotify_client()

    logger.info(f"Downloading playlist {id}...")
    pl = get_full_playlist(sp, id)
    save_playlist(pl, PLAYLISTS_DIR)
    logger.info(f"Playlist '{pl['name']}' saved to {PLAYLISTS_DIR / f'{pl["id"]}.yaml'}")
