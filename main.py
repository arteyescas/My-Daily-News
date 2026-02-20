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
        cache_handler=None # Prevents local cache issues in GitHub Actions
    )

    # Use the Refresh Token to get a fresh Access Token
    if "SPOTIPY_REFRESH_TOKEN" in os.environ:
        auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
    else:
        print("Error: SPOTIPY_REFRESH_TOKEN not found.")
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

    # 3. Time Logic: Get episodes from the last 24 hours
    # This is more robust than matching a single date string
    now = datetime.datetime.now(datetime.timezone.utc)
    one_day_ago = now - datetime.timedelta(hours=24)
    
    track_uris = []

    print(f"Checking for episodes released since {one_day_ago.strftime('%Y-%m-%d %H:%M')} UTC...")

    for show_id in SHOW_IDS:
        try:
            results = sp.show_episodes(show_id, limit=5, market="MX")
            
            if results and 'items' in results:
                for item in results['items']:
                    # Convert Spotify string date to object for comparison
                    release_date = item['release_date']
                    
                    # If Spotify only provides YYYY-MM-DD, we compare strings
                    # If the date matches today OR yesterday, we take it
                    today_str = now.strftime('%Y-%m-%d')
                    yesterday_str = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    
                    if release_date in [today_str, yesterday_str]:
                        print(f"Found: {item['name']} ({release_date})")
                        track_uris.append(item['uri'])
                        break # Only take the LATEST episode per show
        except Exception as e:
            print(f"Skipping show {show_id} due to error: {e}")

    # 4. Update the Playlist
    if track_uris:
        try:
            # We reverse to put the newest at the top
            track_uris.reverse() 
            
            print(f"Attempting to update playlist {PLAYLIST_ID} with {len(track_uris)} tracks...")
            
            # Use the 2026-safe method: Clear then Add
            sp.playlist_replace_items(PLAYLIST_ID, []) # Clear
            sp.playlist_add_items(PLAYLIST_ID, track_uris) # Add fresh
            
            print("✅ Success! Playlist updated.")
        except Exception as e:
            print(f"❌ Failed to update playlist: {e}")
            sys.exit(1)
    else:
        print("No new episodes found in the last 24 hours.")

if __name__ == "__main__":
    main()
