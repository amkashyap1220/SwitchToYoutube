import os

import ytmusicapi
from ytmusicapi import YTMusic

from app import config, matcher


def save_login(headers):
    """Saves the request headers copied from the browser, and checks they work."""
    ytmusicapi.setup(filepath=config.YOUTUBE_AUTH_FILE, headers_raw=headers)
    try:
        YTMusic(config.YOUTUBE_AUTH_FILE).get_library_playlists(limit=1)
    except Exception:
        os.remove(config.YOUTUBE_AUTH_FILE)
        raise


def is_logged_in():
    return os.path.exists(config.YOUTUBE_AUTH_FILE)


def get_client():
    if not is_logged_in():
        return None
    return YTMusic(config.YOUTUBE_AUTH_FILE)


def find_song(youtube, song):
    """Returns the videoId of the song on YouTube Music, or None if it can't be found."""
    query = song["title"] + " " + song["artists"][0]

    # Try official songs first, then music videos.
    video_id = matcher.best_match(song, youtube.search(query, filter="songs", limit=5))
    if video_id is None:
        video_id = matcher.best_match(song, youtube.search(query, filter="videos", limit=5))
    return video_id


def get_or_create_playlist(youtube, name):
    """Reuses a playlist with the same name if one exists, so running twice doesn't make duplicates."""
    for playlist in youtube.get_library_playlists(limit=None):
        if playlist["title"] == name:
            return playlist["playlistId"]
    playlist_id = youtube.create_playlist(name, "Imported from Spotify")
    # On failure ytmusicapi returns the error response instead of an id.
    if not isinstance(playlist_id, str):
        raise Exception("Could not create playlist: " + str(playlist_id))
    return playlist_id


def add_to_playlist(youtube, playlist_id, video_ids):
    # Add in chunks, since very large requests can fail.
    for i in range(0, len(video_ids), 50):
        youtube.add_playlist_items(playlist_id, video_ids[i:i + 50], duplicates=False)
