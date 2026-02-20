import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime

def main():
    # 1. AUTHENTICATION
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    redirect_uri = "http://127.0.0.1:5000/callback" 
    scope = "playlist-modify-public playlist-modify-private user-read-email user-read-private"

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
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
    
    # 3. SEARCH LOGIC (Defining track_uris here)
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    track_uris = []

    print(f"Searching for episodes from {yesterday} and {today}...")

    for sid in SHOW_IDS:
        try:
            results = sp.show_episodes(sid, limit=2, market="MX")
            if results and 'items' in results:
                for item in results['items']:
                    if item['release_date'] in [today, yesterday]:
                        print(f"Found: {item['name']} ({item['release_date']})")
                        track_uris.append(item['uri'])
                        break
        except Exception as e:
            print(f"Skipping show {sid}: {e}")
            continue

    # 4. THE UPDATE
    if track_uris:
        try:
            track_uris.reverse() # Put newest episodes at the top
            print(f"Updating playlist {playlist_id} with {len(track_uris)} tracks...")
            sp.playlist_replace_items(playlist_id, track_uris)
            print("🚀 SUCCESS! Your daily news playlist is updated.")
        except Exception as e:
            print(f"❌ Update failed: {e}")
            sys.exit(1)
    else:
        print("No new episodes found for today or yesterday.")

if __name__ == "__main__":
    main()
