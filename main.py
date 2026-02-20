import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime

def main():
    # 1. AUTHENTICATION
    scope = "playlist-modify-public playlist-modify-private playlist-read-private user-read-email user-read-private"
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri="http://127.0.0.1:5000/callback", 
        scope=scope,
        cache_handler=None
    )

    token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.me()['id']
    
    # 2. TARGET PLAYLIST (Hard-coded name for consistency)
    target_name = "Daily News Summary"
    playlist_id = None
    
    # Force a search for the playlist
    results = sp.current_user_playlists(limit=50)
    for item in results['items']:
        if item['name'] == target_name:
            playlist_id = item['id']
            break

    if not playlist_id:
        print(f"Creating new playlist: {target_name}")
        new_pl = sp.user_playlist_create(user_id, target_name, public=True)
        playlist_id = new_pl['id']
    else:
        print(f"Found existing playlist: {playlist_id}")

    # 3. SEARCH LOGIC
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

    # 4. UPDATE CONTENT AND DESCRIPTION
    if track_uris:
        track_uris.reverse()
        try:
            # We use 'playlist_replace_items' which clears and adds in one go
            sp.playlist_replace_items(playlist_id, track_uris)
            
            # Update Description with Hermosillo Timestamp
            # (Note: GitHub runners use UTC, so we label it accordingly)
            now = datetime.datetime.now()
            new_description = f"Last updated: {now.strftime('%Y-%m-%d %H:%M')} UTC. Fresh news for Lizye."
            sp.playlist_change_details(playlist_id, description=new_description)
            
            print(f"🚀 SUCCESS! Added {len(track_uris)} episodes to {target_name}")
        except Exception as e:
            print(f"❌ Update failed: {e}")
            sys.exit(1)
    else:
        print("No new news found today. Playlist remains as is.")

if __name__ == "__main__":
    main()
