import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

from app import config


def get_auth_manager():
    return SpotifyOAuth(
        client_id=config.SPOTIFY_CLIENT_ID,
        client_secret=config.SPOTIFY_CLIENT_SECRET,
        redirect_uri=config.SPOTIFY_REDIRECT_URI,
        scope=config.SPOTIFY_SCOPE,
        cache_handler=CacheFileHandler(cache_path=config.SPOTIFY_TOKEN_FILE),
        open_browser=False,
    )


def get_client():
    """Returns a Spotify client, or None if we aren't logged in yet."""
    if config.SPOTIFY_CLIENT_ID == "" or config.SPOTIFY_CLIENT_SECRET == "":
        return None

    auth_manager = get_auth_manager()
    token = auth_manager.cache_handler.get_cached_token()
    if auth_manager.validate_token(token) is None:
        return None

    return spotipy.Spotify(auth_manager=auth_manager)


def get_all_items(spotify, page):
    """Spotify returns results in pages. This follows the pages and returns every item."""
    items = []
    while page is not None:
        items.extend(page["items"])
        if page["next"]:
            page = spotify.next(page)
        else:
            page = None
    return items


def to_song(track):
    """Keeps only the fields we need. Returns None for podcast episodes and empty entries."""
    if track is None or track.get("type") != "track":
        return None

    artists = []
    for artist in track["artists"]:
        artists.append(artist["name"])

    if len(artists) == 0:
        artists.append("")

    return {
        "title": track["name"],
        "artists": artists,
        "seconds": track["duration_ms"] // 1000,
    }


def get_playlists(spotify):
    playlists = []
    for playlist in get_all_items(spotify, spotify.current_user_playlists(limit=50)):
        if playlist is None:
            continue
        # Spotify has used both "tracks" and "items" for the song count.
        info = playlist.get("items") or playlist.get("tracks") or {}
        playlists.append({
            "id": playlist["id"],
            "name": playlist["name"],
            "song_count": info.get("total", 0),
        })
    return playlists


def get_liked_songs(spotify):
    songs = []
    for item in get_all_items(spotify, spotify.current_user_saved_tracks(limit=50)):
        song = to_song(item["track"])
        if song is not None:
            songs.append(song)
    return songs


def get_playlist_songs(spotify, playlist_id):
    songs = []
    for item in get_all_items(spotify, spotify.playlist_items(playlist_id, limit=100)):
        # Newer API responses use "item", older ones use "track".
        song = to_song(item.get("item") or item.get("track"))
        if song is not None:
            songs.append(song)
    return songs
