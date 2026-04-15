from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Track:
    name: str
    artist: str
    uri: str
    album: Optional[str] = None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


@dataclass
class Playlist:
    id: str  # Spotify ID
    name: str
    description: str = ""
    public: bool = False
    collaborative: bool = False
    owner_id: str = ""
    tracks: list[Track] = field(default_factory=list)

    def to_dict(self) -> dict[str, str | bool | list[dict[str, str | None]]]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "public": self.public,
            "collaborative": self.collaborative,
            "owner_id": self.owner_id,
            "tracks": [t.to_dict() for t in self.tracks],
        }
