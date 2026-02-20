import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime
import sys

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

    if "SPOTIPY_REFRESH_TOKEN" in os.environ:
        auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
    else:
        print("Error: SPOTIPY_REFRESH_TOKEN missing.")
        sys.exit(1)

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # 2. Configuration
    SHOW_IDS = [
        "5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh",
        "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9",
        "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3",
        "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP",
    ]
    
    PLAYLIST_ID = os.environ.get("TARGET_PLAYLIST_ID")

    # 3. Find Episodes
    now = datetime.datetime.now(datetime.timezone.utc)
    dates = [now.strftime('%Y-%m-%d'), (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')]
    track_uris = []

    for show_id in SHOW_IDS:
        try:
            results = sp.show_episodes(show_id, limit=2, market="MX")
            if results and 'items' in results:
                for item in results['items']:
                    if item['release_date'] in dates:
                        track_uris.append(item['uri'])
                        break 
        except:
            continue

    # 4. THE 2026-SAFE UPDATE
    if track_uris:
        track_uris.reverse()
        print(f"Attempting to update {PLAYLIST_ID} with {len(track_uris)} tracks...")

        try:
            # We fetch the current state of the playlist to get a 'snapshot_id'
            playlist_info = sp.playlist(PLAYLIST_ID)
            print(f"Updating Playlist: {playlist_info['name']} (Owner: {playlist_info['owner']['id']})")

            # STEP A: Try to CLEAR using the most basic method
            try:
                sp.playlist_replace_items(PLAYLIST_ID, [])
            except:
                print("Clear failed, attempting to append instead...")

            # STEP B: ADD items using the POST method
            sp.playlist_add_items(PLAYLIST_ID, track_uris)
            print("✅ SUCCESS! Playlist updated.")
            
        except Exception as e:
            print(f"❌ AUTH ERROR: {e}")
            sys.exit(1)
    else:
        print("No new episodes found today.")

if __name__ == "__main__":
    main()
