import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime

def main():
    # 1. Authentication
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope="playlist-modify-public playlist-modify-private"
    )

    # Refresh the token manually using the environment variable
    if "SPOTIPY_REFRESH_TOKEN" in os.environ:
        auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # 2. Configuration
    # PASTE YOUR OUTPUT FROM get_ids.py HERE
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
    
    PLAYLIST_ID = os.environ["TARGET_PLAYLIST_ID"]

    # 3. Find Today's Episodes
    # We use UTC time because GitHub Actions runs in UTC. 
    # If it's 6AM in Mexico, it's roughly 12PM/1PM UTC, so "today" matches.
    today = datetime.date.today().isoformat()
    track_uris = []

    print(f"Checking for episodes released on {today}...")

    for show_id in SHOW_IDS:
        try:
            # Fetch show details (limit=5 captures multiple daily updates from same show)
            results = sp.show_episodes(show_id, limit=5, market="MX")
            items = results['items']
            
            for item in items:
                # Check if release date matches today
                if item['release_date'] == today:
                    print(f"Found: {item['name']}")
                    track_uris.append(item['uri'])
                    
        except Exception as e:
            print(f"Error fetching show {show_id}: {e}")

    # 4. Update the Playlist
    if track_uris:
        # replace_items wipes the playlist and adds new ones (perfect for a daily mix)
        sp.playlist_replace_items(PLAYLIST_ID, track_uris)
        print(f"Success! Updated playlist with {len(track_uris)} episodes.")
    else:
        print("No new episodes found today.")

if __name__ == "__main__":
    main()
