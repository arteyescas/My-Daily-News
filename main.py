import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTH
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    refresh_token = os.environ["SPOTIPY_REFRESH_TOKEN"]

    # Refresh Token Manually
    auth_res = requests.post("https://accounts.spotify.com/api/token", data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    })
    
    access_token = auth_res.json().get('access_token')
    # Add User-Agent to avoid 'Empty Response' or 403s from GitHub IP addresses
    headers = {
        "Authorization": f"Bearer {access_token}", 
        "Content-Type": "application/json",
        "User-Agent": "MyDailyNewsApp/1.0"
    }
    
    sp = spotipy.Spotify(auth=access_token)
    user_data = sp.me()
    user_id = user_data['id']
    print(f"✅ Verified Account: {user_id}")

    # 2. FIND OR CREATE
    target_name = "Daily News Summary"
    playlist_id = None
    
    # Try to find existing
    try:
        pl_list = sp.current_user_playlists()
        for pl in pl_list['items']:
            if pl['name'] == target_name:
                playlist_id = pl['id']
                break
    except: pass

    if not playlist_id:
        print("Creating playlist via direct POST...")
        create_res = requests.post(
            f"https://api.spotify.com/v1/users/{user_id}/playlists",
            headers=headers,
            json={"name": target_name, "public": True, "description": "Daily News for Lizye"}
        )
        if create_res.status_code not in [200, 201]:
            print(f"❌ Creation Failed: {create_res.status_code} - {create_res.text}")
            sys.exit(1)
        playlist_id = create_res.json()['id']
        print(f"✅ Created New Playlist: {playlist_id}")

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

    # 4. UPDATE
    if track_uris:
        track_uris.reverse()
        # Using the direct access_token we just refreshed
        update_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        update_res = requests.put(update_url, headers=headers, json={"uris": track_uris})
        
        if update_res.status_code in [200, 201]:
            print(f"🚀 SUCCESS! {len(track_uris)} episodes added.")
        else:
            print(f"❌ Final Update Error: {update_res.text}")
    else:
        print("No news found for today.")

if __name__ == "__main__":
    main()
