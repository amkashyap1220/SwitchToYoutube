import os

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
SPOTIFY_SCOPE = "playlist-read-private playlist-read-collaborative user-library-read"

DATA_FOLDER = os.environ.get("DATA_FOLDER", "data")
SPOTIFY_TOKEN_FILE = os.path.join(DATA_FOLDER, "spotify_token.json")
YOUTUBE_AUTH_FILE = os.path.join(DATA_FOLDER, "youtube_auth.json")

# Pause between YouTube Music requests so we don't get rate limited.
REQUEST_DELAY = 0.5
