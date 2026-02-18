import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys

# 1. SETUP - Use your same credentials
CLIENT_ID = "2ee56b2a6844469cb31728502233761e"
CLIENT_SECRET = "da75badeb99a4411959bec12db8c2a57"
REDIRECT_URI = "http://127.0.0.1:8080/" # Must match your Spotify Dashboard

def create_playlist_final():
    print("--- 1. STARTING AUTHENTICATION (NO CACHE) ---")
    
    # We explicitly request modify permissions
    scope = "playlist-modify-public playlist-modify-private user-read-email"
    
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope,
        show_dialog=True,  # Forces the "Agree" screen every time
        cache_handler=None # CRITICAL: Disables saving the token to a file
    )
    
    # Get the Auth URL
    auth_url = sp_oauth.get_authorize_url()
    print(f"\nStep A: Open this URL in your browser:\n{auth_url}\n")
    print("Step B: Click 'Agree'.")
    print("Step C: You will be redirected to a page that might say 'Not Found' or 'This site can't be reached'.")
    print("Step D: COPY the entire URL from your browser address bar and paste it below.")
    
    redirected_url = input("\nPaste the full redirect URL here: ").strip()
    
    try:
        # Exchange the code for a token
        code = sp_oauth.parse_response_code(redirected_url)
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        
        print("\n--- 2. AUTH SUCCESSFUL ---")
        print(f"NEW REFRESH TOKEN (Save for GitHub): {refresh_token}")
        
    except Exception as e:
        print(f"Error getting token: {e}")
        return

    # Create the Spotify Object
    sp = spotipy.Spotify(auth=access_token)
    user = sp.current_user()
    user_id = user['id']
    
    print(f"\n--- 3. VERIFIED USER: {user_id} ---")
    
    # Attempt to Create Playlist
    print("Attempting to create playlist...")
    try:
        playlist = sp.user_playlist_create(
            user=user_id, 
            name="My Daily News (Automated)", 
            public=True, 
            description="Created via Python API - Final Fix"
        )
        print(f"\nSUCCESS! Playlist Created.")
        print(f"NEW TARGET_PLAYLIST_ID: {playlist['id']}")
        
        # Test adding a track to prove write access
        sp.playlist_add_items(playlist['id'], ["spotify:track:4cOdK2wGLETKBW3PvgPWqT"])
        print("Write test passed: Added track to playlist.")
        
    except Exception as e:
        print(f"\nFAILED with error: {e}")
        if "403" in str(e):
             print("\nDIAGNOSIS: The 403 error persists.")
             print("Please double-check that your email is listed in the 'User Management'")
             print("section of the Spotify Developer Dashboard.")

if __name__ == "__main__":
    create_playlist_final()