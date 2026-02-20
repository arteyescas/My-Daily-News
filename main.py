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

    # 3. Find Today's Episodes
    now = datetime.datetime.now(datetime.timezone.utc)
    today_str = now.strftime('%Y-%m-%d')
    yesterday_str = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    track_uris = []

    print(f"Searching for episodes from {yesterday_str} and {today_str}...")

    for show_id in SHOW_IDS:
        try:
            results = sp.show_episodes(show_id, limit=5, market="MX")
            if results and 'items' in results:
                for item in results['items']:
                    if item['release_date'] in [today_str, yesterday_str]:
                        print(f"Found: {item['name']} ({item['release_date']})")
                        track_uris.append(item['uri'])
                        break 
        except Exception as e:
            print(f"Skipping show {show_id}: {e}")

    # 4. THE 2026 "POST ONLY" UPDATE
    if track_uris:
        try:
            track_uris.reverse() 
            print(f"Updating playlist {PLAYLIST_ID} with {len(track_uris)} tracks...")

            # STEP A: REMOVE EVERYTHING (Using POST, not PUT)
            # We use a trick: adding items to a playlist is a POST. 
            # But first we have to clear it. Since PUT is blocked, we use the 'replace' logic 
            # but we force it to use a POST-style call if possible, or just add on top.
            
            try:
                # If this PUT fails, we will just APPEND and you'll have to clear it manually once a week
                sp.playlist_replace_items(PLAYLIST_ID, [])
            except:
                print("Note: Could not clear playlist (PUT blocked). Appending instead.")

            # STEP B: ADD ITEMS (This is a POST request)
            sp.playlist_add_items(PLAYLIST_ID, track_uris)
            
            print("✅ SUCCESS! Playlist updated.")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            sys.exit(1)
    else:
        print("No new episodes found.")

if __name__ == "__main__":
    main()
