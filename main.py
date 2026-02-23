import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTH (Ya verificado y funcionando)
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    refresh_token = os.environ["SPOTIPY_REFRESH_TOKEN"]

    auth_res = requests.post("https://accounts.spotify.com/api/token", data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }).json()
    
    access_token = auth_res.get('access_token')
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # 2. PLAYLIST ID (Usamos el que ya se creó con éxito)
    playlist_id = "7MXLDULKXFmIShFJlNbvgM"

    # 3. BÚSQUEDA DE EPISODIOS
    SHOW_IDS = ["5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", "2vLiCH78iiqtRcQe78ADRt"]
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    track_uris = []

    sp = spotipy.Spotify(auth=access_token)
    for sid in SHOW_IDS:
        try:
            # Respetamos el límite de 10 de la migración 2026
            items = sp.show_episodes(sid, limit=2, market="MX")['items']
            for i in items:
                if i['release_date'] in [today, yesterday]:
                    track_uris.append(i['uri'])
                    break
        except: continue

    # 4. ACTUALIZACIÓN (La clave del 404)
    if track_uris:
        track_uris.reverse()
        print(f"Actualizando {len(track_uris)} episodios en {playlist_id}...")
        
        # En 2026, para evitar el 404 "Service not found", usamos el endpoint /items
        # Pero enviamos los URIs en el cuerpo (body), NO en la URL.
        update_url = f"https://api.spotify.com/v1/...7{playlist_id}/items"
        
        # Intentamos con PUT (Reemplazar todo)
        res = requests.put(update_url, headers=headers, json={"uris": track_uris})
        
        if res.status_code in [200, 201]:
            # Actualizamos descripción
            now_hmo = (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M')
            requests.put(f"https://api.spotify.com/v1/...7{playlist_id}", 
                         headers=headers, 
                         json={"description": f"Sincronizado: {now_hmo} HMO. ¡Listo Perla!"})
            print("🚀 ¡LOGRADO! Tu playlist está actualizada.")
        else:
            print(f"❌ Error Final: {res.status_code} - {res.text}")
    else:
        print("No se encontraron noticias hoy.")

if __name__ == "__main__":
    main()
