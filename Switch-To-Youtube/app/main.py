import os

from flask import Flask, flash, redirect, render_template, request

from app import config, spotify_helper, transfer, youtube_helper

app = Flask(__name__)
app.secret_key = os.urandom(16)  # needed for flash() messages

os.makedirs(config.DATA_FOLDER, exist_ok=True)


@app.route("/")
def index():
    spotify = spotify_helper.get_client()

    playlists = []
    if spotify is not None:
        playlists = spotify_helper.get_playlists(spotify)

    return render_template(
        "index.html",
        has_spotify_keys=config.SPOTIFY_CLIENT_ID != "" and config.SPOTIFY_CLIENT_SECRET != "",
        spotify_connected=spotify is not None,
        youtube_connected=youtube_helper.is_logged_in(),
        playlists=playlists,
    )


@app.route("/spotify/login")
def spotify_login():
    return redirect(spotify_helper.get_auth_manager().get_authorize_url())


@app.route("/callback")
def spotify_callback():
    if "code" not in request.args:
        flash("Spotify login failed: " + request.args.get("error", "unknown error"))
        return redirect("/")

    spotify_helper.get_auth_manager().get_access_token(request.args["code"], as_dict=False, check_cache=False)
    return redirect("/")


@app.route("/youtube/login", methods=["POST"])
def youtube_login():
    try:
        youtube_helper.save_login(request.form["headers"].strip())
    except Exception as e:
        flash("Those headers didn't work: " + str(e))
    return redirect("/")


@app.route("/transfer", methods=["POST"])
def start_transfer():
    if transfer.progress["running"]:
        return redirect("/progress")

    spotify = spotify_helper.get_client()
    youtube = youtube_helper.get_client()
    if spotify is None or youtube is None:
        flash("Connect Spotify and YouTube Music first.")
        return redirect("/")

    playlist_ids = request.form.getlist("playlist")
    include_liked = "liked" in request.form
    if len(playlist_ids) == 0 and not include_liked:
        flash("Pick at least one playlist.")
        return redirect("/")

    transfer.start(spotify, youtube, playlist_ids, include_liked)
    return redirect("/progress")


@app.route("/progress")
def show_progress():
    return render_template("progress.html", progress=transfer.progress)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, threaded=True)
