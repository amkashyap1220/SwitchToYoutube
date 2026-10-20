from difflib import SequenceMatcher

# A search result needs at least this score (0 to 1) to count as the same song.
MIN_SCORE = 0.6


def clean(text):
    """Lowercase, drop anything in brackets like "(feat. X)", and keep only letters, numbers and spaces."""
    text = text.lower()
    if " - " in text:
        # "yesterday - remastered 2009" -> "yesterday"
        text = text.split(" - ")[0]

    result = ""
    depth = 0
    for char in text:
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(depth - 1, 0)
        elif depth == 0 and (char.isalnum() or char == " "):
            result += char
    return " ".join(result.split())


def similarity(a, b):
    return SequenceMatcher(None, clean(a), clean(b)).ratio()


def score(song, result):
    """How well a YouTube Music search result matches a Spotify song."""
    result_artists = ""
    for artist in result.get("artists") or []:
        result_artists += artist["name"] + " "

    title_score = similarity(song["title"], result.get("title", ""))
    main_artist = clean(song["artists"][0])
    if main_artist != "" and main_artist in clean(result_artists):
        artist_score = 1
    else:
        artist_score = similarity(song["artists"][0], result_artists)

    total = 0.6 * title_score + 0.4 * artist_score

    # Very different lengths usually means a live version, remix or a different song.
    if result.get("duration_seconds") and abs(result["duration_seconds"] - song["seconds"]) > 30:
        total -= 0.15

    return total


def best_match(song, results):
    """Returns the videoId of the best result, or None if nothing is close enough."""
    best_id = None
    best_score = MIN_SCORE
    for result in results:
        if not result.get("videoId"):
            continue
        result_score = score(song, result)
        if result_score >= best_score:
            best_id = result["videoId"]
            best_score = result_score
    return best_id
