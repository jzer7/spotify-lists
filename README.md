# Spotify Playlist Utilities

[![Continuous Integration for Python](https://github.com/jzer7/spotify-lists/actions/workflows/ci-python.yml/badge.svg)](https://github.com/jzer7/spotify-lists/actions/workflows/ci-python.yml)

Tools to work with your Spotify playlists.

## Features

- Synchronize your playlists with local YAML files.

## Setup

1. Install dependencies:

   ```sh
   uv sync --dev
   ```

2. Configure environment:

   Copy `.env.example` to `.env` and fill in your Spotify App credentials.
   You can create an app at
   [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

   ```sh
   cp .env.example .env
   ```

   Make sure to add `http://127.0.0.1:8888/callback` as a Redirect URI in
   your Spotify App settings.
   Use `127.0.0.1` instead of `localhost` in Spotify app settings.

3. Run the CLI:

   ```sh
   uv run listify --help
   # or
   uv run python -m spotify_lists --help
   ```

## Usage

Authenticate with Spotify (opens a browser window):

```sh
uv run listify login
```

Show all your playlists:

```sh
uv run listify list
```

Download all playlists to `playlists/` directory:

```sh
uv run listify download --all
```

Or download a specific playlist by ID:

```sh
uv run listify download --id <spotify_playlist_id>
```

Downloaded files are saved as `playlist_<playlist_id>.yaml` under `playlists/`.
```
