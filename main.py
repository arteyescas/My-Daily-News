import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTH
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    refresh_token = os.environ["SPOTIPY_REFRESH_TOKEN"]
    redirect_uri = "http://127.0.0.1:5000/callback"

    # Get a fresh Access Token manually to avoid 401/403 library bugs
    auth_res = requests.post("https://accounts.spotify.com/api/token", data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }).json()
    
    access_token = auth_res.get('access_token')
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    sp = spotipy.Spotify(auth=access_token)
    user_id = sp.me()['id']

    # 2. FIND OR CREATE PLAYLIST
    target_name = "Daily News Summary"
    playlist_id = None
    
    # Check if it exists
    pl_list = sp.current_user_playlists()
    for pl in pl_list['items']:
        if pl['name'] == target_name:
            playlist_id = pl['id']
            break

    if not playlist_id:
        print("Creating playlist via direct POST...")
        create_res = requests.post(
            f"https://api.spotify.com/v1/playlists/{user_id}/playlists",
            headers=headers,
            json={"name": target_name, "public": True}
        )
        if create_res.status_code not in [200, 201]:
            print(f"❌ Creation Failed: {create_res.text}")
            sys.exit(1)
        playlist_id = create_res.json()['id']

    # 3. SEARCH LOGIC (Keeping your existing logic)
    # ... (Search for episodes as before) ...
    # (Assume track_uris is filled here)

    # 4. FINAL ADD
    if track_uris:
        track_uris.reverse()
        # Wipe and Add
        sp.playlist_replace_items(playlist_id, track_uris)
        print("🚀 SUCCESS!")

if __name__ == "__main__":
    main()
