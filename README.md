# Spotify Playlist Utilities

Tools to work with your Spotify playlists.

## Features

- Synchronize your playlists with local YAML files.

## Setup

1.  **Install dependencies**:

    ```bash
    uv sync
    ```

2.  **Configure Environment**:

    Copy `.env.example` to `.env` and fill in your Spotify App credentials.
    You can create an app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

    ```bash
    cp .env.example .env
    ```

    Make sure to add `http://127.0.0.1:8888/callback` as a Redirect URI in your Spotify App settings.
    Note: `localhost` is no longer supported by Spotify; use `127.0.0.1` instead.

## Usage

Authenticate with Spotify (opens a browser window):

```bash
python -m src.cli login
```

Show all your playlists:

```bash
python -m src.cli list
```

Download all playlists to `playlists/` directory:

```bash
python -m src.cli download --all
```

Or download a specific playlist by ID:

```bash
python -m src.cli download --id <spotify_playlist_id>
```
