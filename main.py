import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime
import sys

def main():
    # 1. Authentication
    # We explicitly request the scopes needed to EDIT playlists
    scope = "playlist-modify-public playlist-modify-private"
    
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope=scope
    )

    # Refresh the token manually
    if "SPOTIPY_REFRESH_TOKEN" in os.environ:
        auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
    else:
        print("Error: SPOTIPY_REFRESH_TOKEN not found in environment variables.")
        sys.exit(1)

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # 2. Configuration
    # Ensure this block matches what you generated with get_ids.py
    SHOW_IDS = [
    "5Gka9laolwx0TzJ0biYpxz", # Tu Shot (by Unknown Publisher)
    "6NohCptkHoUdIvgr7d0C43", # Las Noticias del Día (MX) (by Unknown Publisher)
    "6SVAeMaKdzhA9DIY8ZFZTh", # Cafeína x Sopitas.com (by Unknown Publisher)
    "1nS40a6gR0w53seTurNddC", # El Noti (by Unknown Publisher)
    "0vDgnorbpBr65YZzFVVouE", # CNN 5 Cosas (by Unknown Publisher)
    "5X2O35fLXaXrNZUtP48LI9", # Bloomberg Daybreak América Latina (by Unknown Publisher)
    "5ZGlgp8Y6fpXNpg9drwBUs", # Primera Plana: Noticias (by Unknown Publisher)
    "1H5BkWb7cjPE5zQiwnqbqP", # GBM | Markets & News (by Unknown Publisher)
    "1gVuEXINi9lVjt1Ya2DAJ3", # MVS Noticias / Lo más relevante (by Unknown Publisher)
    "2vLiCH78iiqtRcQe78ADRt", # Noticias Univision (by Unknown Publisher)
    "2pXBpdfJoAo2iNz5G25nCP", # AM (by Unknown Publisher)
    ]
    
    PLAYLIST_ID = os.environ.get("TARGET_PLAYLIST_ID")
    if not PLAYLIST_ID:
        print("Error: TARGET_PLAYLIST_ID not found in environment variables.")
        sys.exit(1)

    # 3. Find Today's Episodes
    # Using UTC because GitHub Actions runs in UTC.
    today = datetime.date.today().isoformat()
    track_uris = []

    print(f"Checking for episodes released on {today}...")

    for show_id in SHOW_IDS:
        try:
            # Fetch show details
            results = sp.show_episodes(show_id, limit=5, market="MX")
            
            # FIXED: Check if results exist before accessing items
            if results and 'items' in results:
                items = results['items']
                for item in items:
                    if item['release_date'] == today:
                        print(f"Found: {item['name']}")
                        track_uris.append(item['uri'])
            else:
                print(f"Warning: No data returned for show ID {show_id}")
                    
        except Exception as e:
            # This catches invalid IDs without crashing the whole script
            print(f"Error fetching show {show_id}: {e}")

    # 4. Update the Playlist
    if track_uris:
        try:
            print(f"Attempting to update playlist {PLAYLIST_ID}...")
            sp.playlist_replace_items(PLAYLIST_ID, track_uris)
            print(f"Success! Updated playlist with {len(track_uris)} episodes.")
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 403:
                print("\nCRITICAL ERROR: 403 Forbidden.")
                print("You do not have permission to edit this playlist.")
                print("SOLUTION: Please create a NEW playlist in your Spotify account,")
                print("copy its ID, and update the TARGET_PLAYLIST_ID secret in GitHub.\n")
            else:
                print(f"Spotify API Error: {e}")
            sys.exit(1)
    else:
        print("No new episodes found today.")

if __name__ == "__main__":
    main()
