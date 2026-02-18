import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 1. Fill these in with the EXACT same values you put in GitHub Secrets
CLIENT_ID = "2ee56b2a6844469cb31728502233761e"
CLIENT_SECRET = "da75badeb99a4411959bec12db8c2a57"
REDIRECT_URI = "http://127.0.0.1:8080/" # Must match your Spotify Dashboard

def get_new_token():
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-public playlist-modify-private user-library-read",
        open_browser=True
    )
    
    # This will trigger the browser authentication flow
    token_info = sp_oauth.get_access_token()
    
    print("\n" + "="*30)
    print("NEW REFRESH TOKEN (Copy this):")
    print(token_info['refresh_token'])
    print("="*30 + "\n")

if __name__ == "__main__":
    get_new_token()