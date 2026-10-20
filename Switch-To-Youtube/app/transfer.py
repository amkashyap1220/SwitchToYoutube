import threading
import time

from app import config, spotify_helper, youtube_helper

# Shared with the progress page. Only the transfer thread writes to it.
progress = {
    "running": False,
    "status": "",
    "done": 0,
    "total": 0,
    "results": [],
    "error": None,
}


def start(spotify, youtube, playlist_ids, include_liked):
    progress["running"] = True
    progress["status"] = "Starting"
    progress["done"] = 0
    progress["total"] = 0
    progress["results"] = []
    progress["error"] = None

    thread = threading.Thread(target=run, args=(spotify, youtube, playlist_ids, include_liked), daemon=True)
    thread.start()


def run(spotify, youtube, playlist_ids, include_liked):
    try:
        if include_liked:
            transfer_liked_songs(spotify, youtube)

        names = {}
        for playlist in spotify_helper.get_playlists(spotify):
            names[playlist["id"]] = playlist["name"]

        for playlist_id in playlist_ids:
            transfer_playlist(spotify, youtube, playlist_id, names.get(playlist_id, playlist_id))

        progress["status"] = "Done"
    except Exception as e:
        progress["status"] = "Failed"
        progress["error"] = str(e)
    finally:
        progress["running"] = False


def find_songs(youtube, songs, label):
    """Searches YouTube Music for each song. Returns (video_ids, songs_not_found)."""
    progress["status"] = "Searching for " + label
    progress["done"] = 0
    progress["total"] = len(songs)

    video_ids = []
    not_found = []
    for song in songs:
        try:
            video_id = youtube_helper.find_song(youtube, song)
        except Exception:
            video_id = None

        if video_id is None:
            not_found.append(song["title"] + " - " + ", ".join(song["artists"]))
        elif video_id not in video_ids:
            video_ids.append(video_id)

        progress["done"] += 1
        time.sleep(config.REQUEST_DELAY)

    return video_ids, not_found


def transfer_liked_songs(spotify, youtube):
    progress["status"] = "Reading Liked Songs from Spotify"
    songs = spotify_helper.get_liked_songs(spotify)
    video_ids, not_found = find_songs(youtube, songs, "Liked Songs")

    progress["status"] = "Liking songs"
    progress["done"] = 0
    progress["total"] = len(video_ids)

    # Spotify lists newest first. Like the oldest first so the order matches on YouTube Music.
    for video_id in reversed(video_ids):
        youtube.rate_song(video_id, "LIKE")
        progress["done"] += 1
        time.sleep(config.REQUEST_DELAY)

    progress["results"].append({
        "name": "Liked Songs",
        "found": len(video_ids),
        "total": len(songs),
        "not_found": not_found,
    })


def transfer_playlist(spotify, youtube, playlist_id, name):
    progress["status"] = "Reading " + name + " from Spotify"
    try:
        songs = spotify_helper.get_playlist_songs(spotify, playlist_id)
    except Exception:
        # Spotify's own playlists (Discover Weekly etc.) can't be read through the API.
        progress["results"].append({"name": name, "found": 0, "total": 0, "not_found": [],
                                    "error": "Spotify didn't allow reading this playlist"})
        return

    video_ids, not_found = find_songs(youtube, songs, name)

    if len(video_ids) > 0:
        progress["status"] = "Creating playlist " + name
        yt_playlist_id = youtube_helper.get_or_create_playlist(youtube, name)
        youtube_helper.add_to_playlist(youtube, yt_playlist_id, video_ids)

    progress["results"].append({
        "name": name,
        "found": len(video_ids),
        "total": len(songs),
        "not_found": not_found,
    })
