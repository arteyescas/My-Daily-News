import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime

def main():
    # 1. Authentication with Refresh Token
    # We use a refresh token so this script can run on GitHub without a browser.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope="playlist-modify-public playlist-modify-private",
        open_browser=False,
        cache_handler=None # Disable cache to force refresh
    ))

    # 2. Configuration
    # Replace these with the Spotify IDs of your favorite podcasts
    # (e.g., 'Te lo Cuento', 'Las Noticias del Día MX', etc.)
    SHOW_IDS = [
        "4rOoJ64cGBp78Ko4U56t7n", # Example: Te lo Cuento
        "3zIpqxGvoQkLyySjDq3P95", # Example: Las Noticias del Día MX
        # Add the IDs for your other 12 podcasts here...
    ]
    
    # The ID of the playlist you want to update
    PLAYLIST_ID = os.environ["TARGET_PLAYLIST_ID"]

    # 3. Find Today's Episodes
    today = datetime.date.today().isoformat()
    track_uris = []

    print(f"Checking for episodes released on {today}...")

    for show_id in SHOW_IDS:
        try:
            # Fetch show details to get the latest episodes
            results = sp.show_episodes(show_id, limit=5, market="MX")
            items = results['items']
            
            for item in items:
                # check if release date matches today
                if item['release_date'] == today:
                    print(f"Found: {item['name']}")
                    track_uris.append(item['uri'])
                    
        except Exception as e:
            print(f"Error fetching show {show_id}: {e}")

    # 4. Update the Playlist
    if track_uris:
        # 'replace=True' clears the old episodes and adds the new ones
        sp.playlist_replace_items(PLAYLIST_ID, track_uris)
        print(f"Success! Updated playlist with {len(track_uris)} episodes.")
    else:
        print("No new episodes found today.")

if __name__ == "__main__":
    main()
