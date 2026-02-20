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
    
    # 2. TARGET PLAYLIST
    target_name = "Daily News Summary"
    playlist_id = None
    
    results = sp.current_user_playlists(limit=50)
    for item in results['items']:
        if item['name'] == target_name:
            playlist_id = item['id']
            break

    if not playlist_id:
        print(f"Creating new playlist: {target_name}")
        new_pl = sp.user_playlist_create(user_id, target_name, public=True)
        playlist_id = new_pl['id']

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

    # 4. THE BYPASS UPDATE (Wipe then Add)
    if track_uris:
        track_uris.reverse()
        try:
            # STEP A: GET CURRENT ITEMS
            current_items = sp.playlist_items(playlist_id, fields='items(track(uri))')
            current_uris = [item['track']['uri'] for item in current_items['items'] if item['track']]
            
            # STEP B: REMOVE ALL (Using DELETE method)
            if current_uris:
                sp.playlist_remove_all_occurrences_of_items(playlist_id, current_uris)
                print("Old tracks cleared.")

            # STEP C: ADD NEW (Using POST method)
            sp.playlist_add_items(playlist_id, track_uris)
            
            # STEP D: UPDATE DESCRIPTION
            now_hmo = (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M')
            new_desc = f"Updated: {now_hmo} (HMO). Daily news for Lizye."
            sp.playlist_change_details(playlist_id, description=new_desc)
            
            print(f"🚀 SUCCESS! {len(track_uris)} episodes added to '{target_name}'.")
        except Exception as e:
            print(f"❌ Update failed: {e}")
            sys.exit(1)
    else:
        print("No new news found today.")

if __name__ == "__main__":
    main()
