# Switch To YouTube

Move your music from Spotify to YouTube Music.

Switch To YouTube is a small web app that runs on your own computer and copies your Spotify **Liked Songs** and **playlists** to YouTube Music. No paid service, no account with anyone else.

How it works:

1. You log in to Spotify and YouTube Music.
2. You tick Liked Songs and whichever playlists you want.
3. For each song, the app searches YouTube Music and picks the closest match by title, artist and length.
4. Liked Songs are liked on YouTube Music, in the same order as on Spotify. Each playlist is created on YouTube Music with the same name.
5. At the end you see how many songs were found in each playlist, and a list of the ones that weren't.

Built with Python, Flask, [spotipy](https://spotipy.readthedocs.io/) (Spotify) and [ytmusicapi](https://ytmusicapi.readthedocs.io/) (YouTube Music).

---

## What you need

- **Docker Desktop**: [download it here](https://www.docker.com/products/docker-desktop/) and make sure it's running. On Linux, Docker Engine with the Compose plugin works too.
- A **Spotify** account (free or Premium).
- A **Google account** you use for YouTube Music.
- About 10 minutes for the first-time setup.

---

## Step 1: Create a Spotify app (to get API keys)

Spotify only lets apps read your library if they have their own keys. Creating them is free and takes a few minutes.

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in with your normal Spotify account. Accept the developer terms if asked.
2. Click **Create app** and fill in the form:
   - **App name:** anything, for example `Switch To YouTube`.
   - **App description:** anything.
   - **Redirect URI:** type `http://127.0.0.1:8888/callback` exactly, then click **Add**.
     > Spotify no longer accepts `localhost` here, so it has to be `127.0.0.1`.
   - **Which API/SDKs are you planning to use?** Tick **Web API**.
   - Agree to the terms and click **Save**.
3. On your new app's page, click **Settings**.
4. Copy the **Client ID**.
5. Click **View client secret** and copy the **Client secret** too.

Keep these two values handy for the next step. Treat the secret like a password.

> **"User not registered" error later on?** New Spotify apps are in "development mode", which only lets listed users log in. Open your app in the dashboard, go to **User Management**, and add the name and email of your Spotify account. Spotify sometimes changes the rules for development-mode apps, so if login is still refused, check the dashboard for any notices.

---

## Step 2: Add your keys and start the app

1. Get the code and open a terminal in the project folder:

   ```bash
   git clone https://github.com/amkashyap1220/Switch-To-Youtube.git
   cd Switch-To-Youtube
   ```

   No git? On the GitHub page click **Code → Download ZIP**, unzip it, and open a terminal in the unzipped folder.

2. Make your settings file from the example:

   ```bash
   cp .env.example .env
   ```

   On Windows Command Prompt, use `copy .env.example .env`.

3. Open `.env` in any text editor and paste in your keys:

   ```
   SPOTIFY_CLIENT_ID=paste-your-client-id-here
   SPOTIFY_CLIENT_SECRET=paste-your-client-secret-here
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

4. Build and start the app:

   ```bash
   docker compose up -d --build
   ```

   The first run takes a minute while Docker downloads Python and installs everything.

5. Open **http://127.0.0.1:8888** in your browser.

   > Use `127.0.0.1` rather than `localhost`, so it matches the Spotify redirect address.

If you change `.env` later, run `docker compose up -d` again to pick up the change.

---

## Step 3: Connect Spotify

On the app's page, click **Connect Spotify**. You'll be sent to Spotify. Click **Agree**, and you'll come back to the app with Spotify showing "Connected" and your playlists listed further down.

---

## Step 4: Connect YouTube Music

YouTube Music has no official API for this, so the app logs in the same way your browser does. You copy your browser's request headers once and paste them into the app. It sounds technical, but it takes about a minute.

1. Open [music.youtube.com](https://music.youtube.com) in **Chrome**, **Edge** or **Firefox**, and make sure you're logged in to the account you want the music in.
2. Open the developer tools: press **F12**, or **Cmd + Option + I** on a Mac.
3. Click the **Network** tab.
4. In YouTube Music, click **Library** in the left menu. This creates the request we need.
5. In the Network tab's filter box, type `browse`.
6. Click any request whose name starts with `browse?` and whose method is **POST**. If you can't see the method, click a few until the Headers panel shows `Request Method: POST` and a URL containing `/youtubei/v1/browse`.
7. Copy the **request headers**:
   - **Firefox:** right-click the request, then choose **Copy Value → Copy Request Headers**.
   - **Chrome / Edge:** in the **Headers** panel, scroll down to **Request Headers**. If there's a **Raw** toggle, turn it on. Select everything in that section, from the first line (usually `accept: */*`) to the last, and copy it.
8. Back in the app, paste everything into the box under **2. YouTube Music** and click **Save**.

If it worked, the section will show "Connected". If not, you'll see an error. The most common one is *missing x-goog-authuser*, which means you copied the headers from the wrong request. Try again with a POST request to `/youtubei/v1/browse`.

About this login:

- It stays valid as long as you don't log out of YouTube Music in that browser. If you log out or clear your cookies, the app's login stops working too.
- To log in again, delete the file `data/youtube_auth.json` and refresh the page.
- That file contains your login cookie, so don't share it.
- If you use a YouTube brand account, switch to it in the browser before copying the headers.

---

## Step 5: Choose what to copy and start

1. Under **3. Pick what to copy**:
   - **Liked Songs** is ticked by default. Untick it if you only want playlists.
   - Tick the playlists you want, or tick **Select all**.
   - The number next to each playlist is how many songs it has.
2. Click **Start transfer**.
3. You'll be taken to the progress page, which refreshes every few seconds. It shows what it's doing (for example "Searching for Road Trip" or "Liking songs") and a progress bar.
4. When it's done, each playlist shows **Found X of Y songs**. Click **Not found** to see which songs it couldn't match.

You can close the browser tab while it runs. The transfer keeps going in the background, and you can check on it at http://127.0.0.1:8888/progress.

**How long does it take?** About 1 to 2 seconds per song. 500 songs takes roughly 10 to 15 minutes, and 3,000 songs about an hour or more.

**Where to find the results on YouTube Music:**
- Liked songs: **Library → Liked music**.
- Playlists: **Library → Playlists**. New playlists are private and have the description "Imported from Spotify".

---

## Running it again

Running the app again is safe, for example to pick up new songs or retry after an error:

- Liking a song that's already liked does nothing.
- If a YouTube Music playlist with the same name already exists, songs are added to it rather than a new one being created, and songs already in it are skipped.

So if you rename a playlist on YouTube Music, the next run will create a new one with the Spotify name.

---

## Good to know

- **No API quota to worry about.** The official YouTube Data API only allows about 100 searches a day, which is far too few. ytmusicapi talks to YouTube Music the way the website does, so that quota doesn't apply.
- **YouTube can still slow you down.** Thousands of requests in a row can get temporarily rate-limited. The app pauses 0.5 seconds between requests. For a very large library, raise `REQUEST_DELAY` in `app/config.py` to `1`, or transfer a few playlists at a time.
- **Spotify-made playlists can't be copied directly.** Spotify doesn't let apps read its own playlists, such as Discover Weekly, Release Radar, Daylist or "This Is…". They'll show "Spotify didn't allow reading this playlist". To copy one anyway, open it in Spotify, select all songs (Ctrl/Cmd + A), add them to a new playlist of your own, then transfer that.
- **Matching isn't perfect.** Remixes, live versions, covers and songs that aren't on YouTube Music may be missed or matched to a different version. If a song isn't found as an official song, the app falls back to music videos.
- **Podcast episodes** in playlists are skipped.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| Page says to add your Spotify keys | `.env` is missing or empty. Fill it in (Step 2) and run `docker compose up -d`. |
| Spotify shows `INVALID_CLIENT: Invalid redirect URI` | The Redirect URI in the Spotify dashboard must be exactly `http://127.0.0.1:8888/callback`, the same as in `.env`. |
| Spotify says the user isn't registered | Add your account under **User Management** in your Spotify app (see Step 1). |
| "Those headers didn't work" | Copy the headers again from a **POST** request to `/youtubei/v1/browse` while logged in (Step 4). |
| YouTube Music stopped working after a while | Your browser session ended. Delete `data/youtube_auth.json`, refresh, and paste fresh headers. |
| The transfer failed partway through | The error is shown on the progress page. Often it's rate limiting: wait a while, then start again. Finished playlists won't be duplicated. |
| Port 8888 is already in use | Change `127.0.0.1:8888:8888` in `docker-compose.yml` to `127.0.0.1:9000:8888`, and change the redirect URI to `http://127.0.0.1:9000/callback` in both `.env` and the Spotify dashboard. |
| Something else | Check the logs with `docker compose logs -f`. |

---

## Stopping, updating and resetting

- **Stop the app:** `docker compose down`
- **Start it again:** `docker compose up -d`
- **After changing the code:** `docker compose up -d --build`
- **Log out of everything:** delete the `data` folder. It only holds your Spotify and YouTube login files.

---

## Running without Docker

You need Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export SPOTIFY_CLIENT_ID=...       # Windows: set SPOTIFY_CLIENT_ID=...
export SPOTIFY_CLIENT_SECRET=...
python -m app.main
```

Then open http://127.0.0.1:8888.

---

## Project layout

```
Switch-To-Youtube/
├── app/
│   ├── main.py             Flask routes (the web pages)
│   ├── config.py           settings and file paths
│   ├── spotify_helper.py   Spotify login and reading playlists / liked songs
│   ├── youtube_helper.py   YouTube Music login, searching, playlists
│   ├── matcher.py          picks the best search result for a song
│   ├── transfer.py         runs the transfer in a background thread
│   ├── templates/          HTML pages
│   └── static/style.css
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

This uses an unofficial YouTube Music API and is meant for personal use with your own account.
