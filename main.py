import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime

def main():
    # 1. AUTHENTICATION (The "Master" Scopes)
    scope = "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-read-email user-read-private"
    
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope=scope,
        cache_handler=None
    )
    
    try:
        token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_id = sp.me()['id']
        print(f"Logged in as: {user_id}")
    except Exception as e:
        print(f"❌ AUTH FAILED: {e}")
        sys.exit(1)

    # 2. FIND OR CREATE THE PLAYLIST
    target_name = "Daily News Summary"
    playlist_id = None
    
    try:
        # This is where it failed before - now we have the 'read' scope
        user_playlists = sp.current_user_playlists()
        for pl in user_playlists['items']:
            if pl['name'] == target_name:
                playlist_id = pl['id']
                break
    except Exception as e:
        print(f"⚠️ Could not list playlists: {e}")

    if not playlist_id:
        print(f"Creating new playlist: {target_name}")
        new_pl = sp.user_playlist_create(user_id, target_name, public=True)
        playlist_id = new_pl['id']

    # 3. SEARCH (Your search logic is already perfect)
    SHOW_IDS = ["5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"]
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

    # 4. FINAL UPDATE
    if track_uris:
        track_uris.reverse()
        try:
            print(f"Updating {playlist_id}...")
            sp.playlist_replace_items(playlist_id, track_uris)
            print("✅ SUCCESS!")
        except Exception as e:
            print(f"❌ FINAL ERROR: {e}")
    else:
        print("No news found today.")

if __name__ == "__main__":
    main()
