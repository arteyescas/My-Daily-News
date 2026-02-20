import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTHENTICATION & REFRESH
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    refresh_token = os.environ["SPOTIPY_REFRESH_TOKEN"]
    playlist_id = os.environ["TARGET_PLAYLIST_ID"]
    
    # Obtenemos un Access Token fresco manualmente para evitar errores de librería
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(auth_url, data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    })
    
    if auth_response.status_code != 200:
        print(f"❌ Error refrescando token: {auth_response.text}")
        sys.exit(1)
        
    access_token = auth_response.json().get('access_token')
    sp = spotipy.Spotify(auth=access_token)

    # 2. BÚSQUEDA DE EPISODIOS (Tu lógica ya es perfecta)
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

    # 3. ACTUALIZACIÓN MANUAL (POST BYPASS)
    if track_uris:
        track_uris.reverse()
        print(f"Intentando actualizar playlist {playlist_id} con {len(track_uris)} tracks...")
        
        # Usamos la API de Spotify directamente con un POST (más seguro que PUT)
        # Primero: Borramos (Clear)
        header = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Intentamos REEMPLAZAR (PUT) pero con manejo de error manual
        replace_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        res = requests.put(replace_url, headers=header, json={"uris": track_uris})

        if res.status_code in [200, 201]:
            print("✅ ¡LOGRADO! Playlist actualizada con éxito.")
        else:
            print(f"❌ ERROR MANUAL {res.status_code}: {res.text}")
            if "Insufficient client scope" in res.text:
                print("\nACCION REQUERIDA: Tu Refresh Token NO TIENE los permisos de escritura.")
                print("Por favor, genera uno nuevo con: scope = 'playlist-modify-public playlist-modify-private'")
            sys.exit(1)
    else:
        print("No se encontraron episodios nuevos.")

if __name__ == "__main__":
    main()
