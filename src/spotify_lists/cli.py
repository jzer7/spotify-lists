import logging
from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.table import Table

from .auth import get_spotify_client
from .fetch import get_all_playlists, get_one_playlist
from .io import save_playlist

console = Console()
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
    try:
        sp = get_spotify_client()
        user = sp.current_user()
        if not user or "id" not in user:
            logger.error("Failed to retrieve user information after login.")
            return
        logger.info(f"Logged in as {user['display_name']} ({user['id']})")
    except Exception as e:
        logger.error(f"Login failed: {e}")


@cli.command("list")
def list_playlists() -> None:
    """List all Spotify playlists."""
    sp = get_spotify_client()
    playlists = get_all_playlists(sp, get_tracks=False)

    table = Table(title="My Playlists", box=box.SIMPLE)
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="dim")
    table.add_column("Owner ID", style="dim")
    table.add_column("Tracks", justify="right")
    table.add_column("Public", justify="center")

    for pl in playlists:
        table.add_row(pl.name, pl.id, pl.owner_id, str(pl.tracks_total), "Yes" if pl.public else "No")

    console.print(table)


@cli.command()
@click.option("--id", help="Playlist ID to download")
@click.option("--all", "download_all", is_flag=True, help="Download all playlists")
def download(id: str | None, download_all: bool) -> None:
    """Download playlists to local YAML files."""
    sp = get_spotify_client()

    if id:
        logger.info(f"Downloading playlist {id}...")
        pl = get_one_playlist(sp, id)
        save_playlist(pl, PLAYLISTS_DIR)
        logger.info(f"Playlist '{pl.name}' saved to {PLAYLISTS_DIR / f'{pl.id}.yaml'}")
        return

    if download_all:
        playlists = get_all_playlists(sp, get_tracks=False)
        with click.progressbar(playlists, label="Downloading playlists") as bar:
            for pli in bar:
                try:
                    pl = get_one_playlist(sp, pli.id)
                    save_playlist(pl, PLAYLISTS_DIR)
                except Exception as e:
                    logger.error(f"Failed to download playlist {pli.name} ({pli.id}): {e}")
        logger.info(f"Downloaded {len(playlists)} playlists.")
    else:
        logger.error("Please specify --id or --all")
