import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime

def main():
    # 1. AUTHENTICATION
    scope = "playlist-modify-public playlist-modify-private user-read-email user-read-private"
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri="http://127.0.0.1:5000/callback", 
        scope=scope,
        cache_handler=None
    )

    try:
        token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
        sp = spotipy.Spotify(auth=token_info['access_token'])
        print(f"✅ Connection verified for: {sp.me()['id']}")
    except Exception as e:
        print(f"❌ Auth Refresh Failed: {e}")
        sys.exit(1)

    # 2. CONFIGURATION
    playlist_id = os.environ["TARGET_PLAYLIST_ID"]
    SHOW_IDS = [
        "5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", 
        "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", 
        "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", 
        "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"
    ]
    
    # 3. SEARCH LOGIC
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    track_uris = []

    for sid in SHOW_IDS:
        try:
            results = sp.show_episodes(sid, limit=2, market="MX")
            if results and 'items' in results:
                for item in results['items']:
                    if item['release_date'] in [today, yesterday]:
                        track_uris.append(item['uri'])
                        break
        except: continue

    # 4. THE 2026-SAFE UPDATE (Wipe then Add)
    if track_uris:
        track_uris.reverse()
        print(f"Updating playlist {playlist_id}...")
        try:
            # Step A: Clear existing tracks (using DELETE logic instead of PUT)
            current_tracks = sp.playlist_items(playlist_id, fields='items(track(uri))')
            current_uris = [item['track']['uri'] for item in current_tracks['items'] if item['track']]
            
            if current_uris:
                # Remove all items (POST/DELETE method)
                sp.playlist_remove_all_occurrences_of_items(playlist_id, current_uris)
                print("Existing tracks removed.")

            # Step B: Add new tracks (POST method)
            sp.playlist_add_items(playlist_id, track_uris)
            print("🚀 SUCCESS! Your daily news is ready.")
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            sys.exit(1)
    else:
        print("No new episodes found.")

if __name__ == "__main__":
    main()
