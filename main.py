import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime

def main():
    # 1. AUTHENTICATION
    scope = "playlist-modify-public playlist-modify-private user-read-email user-read-private"
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope=scope,
        cache_handler=None
    )
    
    # Refresh token
    token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    PLAYLIST_ID = os.environ["TARGET_PLAYLIST_ID"]
    
    # 2. PODCAST LIST
    SHOW_IDS = [
        "5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", 
        "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", 
        "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", 
        "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"
    ]
    
    # 3. DATE LOGIC
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
                        print(f"Found: {item['name']}")
                        track_uris.append(item['uri'])
                        break
        except: continue

    # 4. THE 2026-SAFE UPDATE (No PUT allowed)
    if track_uris:
        track_uris.reverse()
        print(f"Updating playlist with {len(track_uris)} tracks...")
        
        try:
            # STEP A: CLEAR THE PLAYLIST (Using a specific item removal)
            # We get current tracks first
            current_tracks = sp.playlist_tracks(PLAYLIST_ID, fields="items(track(uri))")
            current_uris = [t['track']['uri'] for t in current_tracks['items'] if t['track']]
            
            if current_uris:
                # This uses DELETE instead of PUT
                sp.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, current_uris)
                print("Playlist cleared.")

            # STEP B: ADD NEW TRACKS (Using POST)
            sp.playlist_add_items(PLAYLIST_ID, track_uris)
            print("✅ SUCCESS! Your daily news is ready.")
            
        except Exception as e:
            print(f"❌ ERROR at update: {e}")
            sys.exit(1)
    else:
        print("No new episodes found.")

if __name__ == "__main__":
    main()
