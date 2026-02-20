import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime

def main():
    # 1. AUTHENTICATION
    # Use the EXACT Redirect URI from your dashboard
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    redirect_uri = "http://127.0.0.1:5000/callback" 
    scope = "playlist-modify-public playlist-modify-private user-read-email user-read-private"

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_handler=None
    )

    try:
        token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
        sp = spotipy.Spotify(auth=token_info['access_token'])
        print(f"✅ Connection verified for: {sp.me()['id']}")
    except Exception as e:
        print(f"❌ Auth Refresh Failed: {e}")
        sys.exit(1)

    # 2. TARGET PLAYLIST
    playlist_id = os.environ["TARGET_PLAYLIST_ID"]
    
    # 3. SEARCH LOGIC (Your logic works, keeping it as is)
    # ... (Your show loop here) ...

    # 4. THE 2026-SAFE UPDATE
    if track_uris:
        try:
            print(f"Updating playlist {playlist_id}...")
            # We use 'playlist_replace_items' which is a single POST/PUT transaction
            sp.playlist_replace_items(playlist_id, track_uris)
            print("🚀 SUCCESS! Check your Spotify app.")
        except Exception as e:
            print(f"❌ Update failed even after whitelist: {e}")
            print("Check if the playlist is 'Collaborative' (it shouldn't be).")
            sys.exit(1)

if __name__ == "__main__":
    main()
