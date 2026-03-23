from pathlib import Path

import yaml

from .models import Playlist


def save_playlist(playlist: Playlist, directory: Path) -> None:
    """Saves a playlist to a YAML file in the specified directory."""
    directory.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = "".join([c for c in playlist.name if c.isalpha() or c.isdigit() or c == " "]).strip()
    if not safe_name:
        safe_name = f"playlist_{playlist.id}"
    filename = directory / f"{safe_name}.yaml"

    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(playlist.to_dict(), f, sort_keys=False, allow_unicode=True)
