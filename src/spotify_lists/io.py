from pathlib import Path

import yaml

from .models import Playlist


def save_playlist(playlist: Playlist, directory: Path) -> None:
    """Saves a playlist as a YAML file.

    The filename uses the format "playlist_{playlist_id}.yaml".
    The function ensures the directory exists and overwrites
    any existing file with the same name.

    Returns:
        None
    """
    directory.mkdir(parents=True, exist_ok=True)

    # Name is "playlist_{id}.yaml"
    filename = f"playlist_{playlist.id}.yaml"
    filepath = directory / filename

    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(playlist.to_dict(), f, sort_keys=False, allow_unicode=True)
