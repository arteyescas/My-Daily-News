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
    
    token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    # 2. FIND OR CREATE THE PLAYLIST
    # We look for a playlist we've created before to avoid 403 on specific IDs
    user_id = sp.me()['id']
    target_name = "Daily News Summary"
    playlist_id = None
    
    print(f"Logged in as: {user_id}")
    
    user_playlists = sp.current_user_playlists()
    for pl in user_playlists['items']:
        if pl['name'] == target_name:
            playlist_id = pl['id']
            break
            
    if not playlist_id:
        print(f"Playlist '{target_name}' not found. Creating a new one...")
        new_pl = sp.user_playlist_create(user_id, target_name, public=True, description="Updated daily by AI")
        playlist_id = new_pl['id']

    # 3. SEARCH LOGIC (Your logic is working perfectly)
    SHOW_IDS = [
        "5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", 
        "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", 
        "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", 
        "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"
    ]
    
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    track_uris = []

    for sid in SHOW_IDS:
        try:
            items = sp.show_episodes(sid, limit=2, market="MX")['items']
            for i in items:
                if i['release_date'] in [today, yesterday]:
                    track_uris.append(i['uri'])
                    break
        except: continue

    # 4. UPDATE (Using the ID we just verified)
    if track_uris:
        track_uris.reverse()
        try:
            print(f"Updating '{target_name}' ({playlist_id}) with {len(track_uris)} tracks...")
            # Using replace_items on a playlist we JUST verified/created
            sp.playlist_replace_items(playlist_id, track_uris)
            print("✅ SUCCESS!")
        except Exception as e:
            print(f"❌ Update failed: {e}")
            sys.exit(1)
    else:
        print("No episodes found today.")

if __name__ == "__main__":
    main()
