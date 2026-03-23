import logging
from pathlib import Path

import click

from src.auth import get_spotify_client
from src.fetch import get_all_playlists_metadata

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
