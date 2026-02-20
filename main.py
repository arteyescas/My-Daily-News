import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime
import sys
import requests

def main():
    # 1. Authentication
    scope = "playlist-modify-public playlist-modify-private user-read-email"
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope=scope,
        cache_handler=None
    )

    try:
        token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token)
    except Exception as e:
        print(f"Auth Failed: {e}")
        sys.exit(1)

    # 2. Configuration & Search
    SHOW_IDS = [
        "5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh",
        "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9",
        "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3",
        "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP",
    ]
    PLAYLIST_ID = os.environ.get("TARGET_PLAYLIST_ID")
    
    now = datetime.datetime.now(datetime.timezone.utc)
    dates = [now.strftime('%Y-%m-%d'), (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')]
    track_uris = []

    print(f"--- Searching for episodes ({dates[1]} to {dates[0]}) ---")
    for show_id in SHOW_IDS:
        try:
            results = sp.show_episodes(show_id, limit=2, market="MX")
            if results and 'items' in results:
                for item in results['items']:
                    if item['release_date'] in dates:
                        print(f"Found: {item['name']}")
                        track_uris.append(item['uri'])
                        break 
        except: continue

    # 4. THE 2026 BYPASS UPDATE (DELETE THEN POST)
    if track_uris:
        track_uris.reverse()
        print(f"\n--- Updating Playlist: {PLAYLIST_ID} ---")
        
        endpoint = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # STEP A: DELETE ALL CURRENT TRACKS
        # In 2026, 'PUT' is often blocked, but 'DELETE' is usually allowed.
        try:
            # We get current tracks to delete them specifically
            current = sp.playlist_tracks(PLAYLIST_ID, fields="items(track(uri))")
            current_uris = [t['track']['uri'] for t in current['items'] if t['track']]
            if current_uris:
                requests.delete(endpoint, headers=headers, json={"tracks": [{"uri": u} for u in current_uris]})
                print("Step A: Existing tracks cleared.")
        except Exception as e:
            print(f"Warning: Could not clear tracks: {e}")

        # STEP B: ADD NEW TRACKS (POST)
        response = requests.post(endpoint, headers=headers, json={"uris": track_uris})

        if response.status_code in [200, 201]:
            print("\n✅ SUCCESS! News playlist is updated.")
        else:
            print(f"\n❌ FINAL ERROR {response.status_code}: {response.text}")
            sys.exit(1)
    else:
        print("\nNo new episodes found.")

if __name__ == "__main__":
    main()
