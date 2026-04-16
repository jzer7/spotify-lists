# Agent Instructions

This file guides AI agents working in this repository.

## Project Overview

`spotify-lists` is a CLI tool for downloading and managing Spotify playlists as YAML files.
The entry point is the `listify` command, backed by a Click CLI in `src/spotify_lists/cli.py`.

## Repository Layout

```
src/spotify_lists/   # Application source code
  auth.py            # Spotify OAuth authentication
  cli.py             # Click CLI commands
  fetch.py           # Spotify API data fetching and mapping
  io.py              # Playlist persistence (YAML read/write)
  models.py          # Dataclasses: Track, Playlist
tests/               # pytest unit tests (currently empty — add tests here)
playlists/           # Downloaded playlists as YAML files (git-tracked)
stubs/spotipy/       # Type stubs for spotipy (not covered by typeshed)
```

## Technology Stack

| Tool | Purpose |
|------|---------|
| Python 3.12+ | Language |
| uv | Dependency and virtual environment management |
| ruff | Linting and formatting |
| mypy | Static type checking |
| pytest + pytest-cov | Testing and coverage |
| make | Task runner |

## Environment Setup

```bash
uv sync --dev          # Install all dependencies including dev
cp .env.example .env   # Fill in Spotify API credentials
```

Required environment variables (see `.env.example`):

- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI`

## Common Commands

```bash
make check        # Lint (ruff), type check (mypy), unit tests — fast feedback loop
make check-all    # Full static analysis + all tests
make test-unit    # Unit tests only
make test-e2e     # End-to-end test against live Spotify API
make ruff         # Lint with ruff
make mypy         # Type check with mypy
make clean        # Remove build artifacts and caches
```

Run the CLI directly:

```bash
uv run listify --help
uv run listify list
uv run listify download --id <spotify_playlist_id>
```

## Coding Conventions

### Type Hints

All functions and methods must have full type annotations. mypy is configured in strict mode — no untyped defs, no implicit `Any`. Follow the existing patterns:

```python
# Good
def get_playlist(sp: Spotify, playlist_id: str) -> Playlist | None: ...

# Bad — missing annotations
def get_playlist(sp, playlist_id): ...
```

### Dependency Injection

Pass dependencies (e.g. `Spotify` client) as function parameters rather than constructing them inside functions. This keeps code testable and decoupled from authentication concerns.

```python
# Good — caller provides the client
def get_one_playlist(sp: Spotify, playlist_id: str) -> Playlist | None: ...

# Bad — function owns its own client
def get_one_playlist(playlist_id: str) -> Playlist | None:
    sp = get_spotify_client()
    ...
```

### DRY / YAGNI

- Extract shared logic only when it is used in two or more places.
- Do not add abstractions, base classes, or parameters for hypothetical future use cases.
- Prefer flat, readable functions over deep class hierarchies.

### Models

Data models live in `models.py` as `@dataclass` classes. Use `field(default_factory=...)` for mutable defaults. Each model provides a `to_dict()` method for serialization.

### Error Handling

Validate external data (API responses, YAML files) at system boundaries. Use explicit `if` checks and return `None` or raise descriptive exceptions. Do not swallow exceptions silently.

### Logging

Use `logging.getLogger(__name__)` in each module. Do not use `print()` for program output — use `rich.Console` in CLI code only.

### Line Length

Maximum 120 characters (configured in `pyproject.toml` under `[tool.ruff]`).

## Testing

- Tests go in `tests/`.
- Use `pytest` with `pytest-mock` for mocking (`mocker` fixture).
- Coverage threshold is 80% (`--cov-fail-under=80.0`).
- Mark slow tests with `@pytest.mark.slow`.
- Do not test private helpers directly; test through the public API.

## What to Avoid

- Do not commit secrets or credentials; use environment variables via `.env`.
- Do not call `get_spotify_client()` inside library functions — inject `sp: Spotify` instead.
- Do not add `# type: ignore` without a comment explaining why.
- Do not modify files under `sandbox.skip/` or `related.skip` — they are excluded from the main project.
- Do not open a browser or make real network calls in unit tests; mock `spotipy.Spotify`.
