import logging

import click

from src.auth import get_spotify_client

@click.group()
def cli() -> None:
    """Spotify playlist utility."""
    pass


@cli.command()
def login() -> None:
    """Authenticate with Spotify."""
    sp = get_spotify_client()
    user = sp.current_user()
    logging.info(f"Logged in as {user['display_name']} ({user['id']})")
