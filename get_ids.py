import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

def get_ids():
    # Authentication (same as your main script)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
        scope="user-library-read", # Simple scope just for searching
        open_browser=True
    ))

    # Your list of 10 specific podcasts
    podcast_names = [
        "Tu Shot",
        "Las Noticias del Día (MX)",
        "Cafeína x Sopitas.com",
        "La Estrategia del dia Mexico",
        "CNN 5 Cosas",
        "Bloomberg Daybreak América Latina",
        "Primera Plana: Noticias",
        "GBM | Markets & News",
        "MVS Noticias / Lo más relevante",
        "Noticias Univision",
        "AM" # Note: This might return multiple results, the script picks the top one
    ]

    print("SHOW_IDS = [")
    
    for name in podcast_names:
        # Search for the show
        results = sp.search(q=name, type='show', limit=1, market="MX")
        shows = results['shows']['items']
        
        if shows:
            show = shows[0]
            # FIXED: Use .get() to avoid crashing if 'publisher' is missing
            publisher = show.get("publisher", "Unknown Publisher")
            print(f'    "{show["id"]}", # {show["name"]} (by {publisher})')
        else:
            print(f'    # ??? Could not find: {name}')
            
    print("]")

if __name__ == "__main__":
    get_ids()