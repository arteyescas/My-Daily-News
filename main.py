import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime

def main():
    # 1. Authentication
    # We define the auth manager inside main
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope="playlist-modify-public playlist-modify-private"
    )

    # Refresh the token manually using the environment variable
    # This updates the internal state of auth_manager
    auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])

    # FIXED: This line is now indented so it is inside main() 
    # and can see 'auth_manager'
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # 2. Configuration
    # Replace these with your actual Podcast IDs
    SHOW_IDS = [
        "4rOoJ64cGBp78Ko4U56t7n", # Example: Te lo Cuento
        "3zIpqxGvoQkLyySjDq3P95", # Example: Las Noticias del Día MX
        # Add your other IDs here...
    ]
    
    PLAYLIST_ID = os.environ["TARGET_PLAYLIST_ID"]

    # 3. Find Today's Episodes
    # Note: GitHub servers run on UTC time. 
    today = datetime.date.today().isoformat()
    track_uris = []

    print(f"Checking for episodes released on {today}...")

    for show_id in SHOW_IDS:
        try:
            # Fetch show details to get the latest episodes
            # market="MX" helps ensure you get the version available in your region
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
        sp.playlist_replace_items(PLAYLIST_ID, track_uris)
        print(f"Success! Updated playlist with {len(track_uris)} episodes.")
    else:
        print("No new episodes found today.")

if __name__ == "__main__":
    main()
