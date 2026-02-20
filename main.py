import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import datetime
import sys
import requests

def main():
    # 1. AUTHENTICATION
    # We use SpotifyOAuth just to handle the token refresh logic
    scope = "playlist-modify-public playlist-modify-private user-read-email"
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope=scope,
        cache_handler=None
    )

    try:
        token_info = auth_manager.refresh_access_token(os.environ["SPOTIPY_REFRESH_TOKEN"])
        access_token = token_info['access_token']
    except Exception as e:
        print(f"Failed to refresh token: {e}")
        sys.exit(1)

    # We still use spotipy for the SEARCH part (reading is working fine)
    sp = spotipy.Spotify(auth=access_token)

    # 2. CONFIGURATION
    SHOW_IDS = [
        "5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh",
        "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9",
        "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3",
        "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP",
    ]
    PLAYLIST_ID = os.environ.get("TARGET_PLAYLIST_ID")

    # 3. FIND EPISODES
    now = datetime.datetime.now(datetime.timezone.utc)
    dates = [now.strftime('%Y-%m-%d'), (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')]
    track_uris = []

    print(f"--- SEARCHING FOR NEWS ({dates[1]} to {dates[0]}) ---")

    for show_id in SHOW_IDS:
        try:
            results = sp.show_episodes(show_id, limit=2, market="MX")
            if results and 'items' in results:
                for item in results['items']:
                    if item['release_date'] in dates:
                        print(f"Found: {item['name']}")
                        track_uris.append(item['uri'])
                        break 
        except Exception:
            continue

    # 4. THE MANUAL OVERRIDE (RAW HTTP POST)
    if track_uris:
        # Reverse to put newest on top
        track_uris.reverse()
        print(f"\n--- ATTEMPTING RAW UPDATE TO PLAYLIST: {PLAYLIST_ID} ---")
        
        # We define the endpoint and headers manually
        endpoint = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # STEP A: CLEAR (Using PUT with an empty list)
        print("Step A: Clearing playlist...")
        requests.put(endpoint, headers=headers, json={"uris": []})

        # STEP B: ADD (Using POST)
        print(f"Step B: Adding {len(track_uris)} tracks...")
        response = requests.post(endpoint, headers=headers, json={"uris": track_uris})

        if response.status_code in [200, 201]:
            print("\n✅ SUCCESS! The manual bypass worked. Your news is ready.")
        else:
            print(f"\n❌ FINAL ERROR {response.status_code}: {response.text}")
            print("\nIf you see 403 here, Spotify is blocking the App's write-access entirely.")
            print("Action: Ensure your playlist 'Morning News' is set to PUBLIC.")
            sys.exit(1)
    else:
        print("\nNo new episodes found to add.")

if __name__ == "__main__":
    main()
