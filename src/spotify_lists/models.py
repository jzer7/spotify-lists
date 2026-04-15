from dataclasses import asdict, dataclass, field


@dataclass
class Track:
    id: str  # Spotify ID
    name: str
    artists: str
    uri: str
    album: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class Playlist:
    id: str  # Spotify ID
    owner_id: str
    name: str
    description: str = ""
    public: bool = False
    collaborative: bool = False
    tracks_total: int = 0
    tracks: list[Track] = field(default_factory=list)

    def to_dict(self) -> dict[str, str | bool | list[dict[str, str]]]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "public": self.public,
            "collaborative": self.collaborative,
            "owner_id": self.owner_id,
            "tracks": [t.to_dict() for t in self.tracks],
        }
