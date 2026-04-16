class SpotifyException(Exception):
    http_status: int
    code: int | None
    msg: str
    reason: str | None

    def __init__(
        self,
        http_status: int,
        code: int | None,
        msg: str,
        reason: str | None = ...,
        headers: dict[str, str] | None = ...,
    ) -> None: ...
