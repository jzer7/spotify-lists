from pathlib import Path

import yaml

from src.models import Playlist


def save_playlist(playlist: Playlist, directory: Path) -> None:
    """Saves a playlist to a YAML file in the specified directory."""
    directory.mkdir(parents=True, exist_ok=True)
    filename = directory / f"{playlist.name}.yaml"

    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(playlist.to_dict(), f, sort_keys=False, allow_unicode=True)
