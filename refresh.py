import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Fill these in with your app details
sp_oauth = SpotifyOAuth(
    client_id="2ee56b2a6844469cb31728502233761e",
    client_secret="da75badeb99a4411959bec12db8c2a57",
    redirect_uri="http://127.0.0.1:8080/", # Must match your Spotify Dashboard
    scope="playlist-modify-public playlist-modify-private"
)

# This will open your browser to auth, then give you the token info
token_info = sp_oauth.get_access_token()
print("YOUR REFRESH TOKEN:", token_info['refresh_token'])