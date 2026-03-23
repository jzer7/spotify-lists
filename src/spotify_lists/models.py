from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Track:
    name: str
    artist: str
    uri: str
    album: Optional[str] = None


@dataclass
class Playlist:
    id: str  # Spotify ID
    name: str
    description: str = ""
    public: bool = False
    tracks: list[Track] = field(default_factory=list)
