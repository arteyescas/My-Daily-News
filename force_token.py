import spotipy
from spotipy.oauth2 import SpotifyOAuth

# REPLACE WITH YOUR APP DETAILS
CLIENT_ID = "2ee56b2a6844469cb31728502233761e"
CLIENT_SECRET = "da75badeb99a4411959bec12db8c2a57"
REDIRECT_URI = "http://127.0.0.1:8080/" 

def get_new_token():
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        # We request these specific permissions
        scope="playlist-modify-public playlist-modify-private user-library-read",
        # THIS IS THE KEY FIX: Forces the "Agree" dialog to appear
        show_dialog=True 
    )
    
    print("Opening browser... Please CLICK AGREE to the permissions.")
    token_info = sp_oauth.get_access_token()
    
    print("\n" + "="*30)
    print("NEW REFRESH TOKEN (Copy this):")
    print(token_info['refresh_token'])
    print("="*30 + "\n")

if __name__ == "__main__":
    get_new_token()