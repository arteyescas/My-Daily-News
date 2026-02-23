import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTENTICACIÓN
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    refresh_token = os.environ["SPOTIPY_REFRESH_TOKEN"]

    # Refresco manual del token
    auth_url = "https://accounts.spotify.com/api/token"
    auth_res = requests.post(auth_url, data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    })
    
    if auth_res.status_code != 200:
        print(f"❌ Error de Auth: {auth_res.text}")
        sys.exit(1)
        
    access_token = auth_res.json().get('access_token')
    headers = {
        "Authorization": f"Bearer {access_token}", 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0" # Identificador para evitar bloqueos de seguridad
    }
    
    # 2. BUSCAR O CREAR PLAYLIST (Endpoint 2026)
    target_name = "Daily News Summary"
    playlist_id = None
    
    print("Obteniendo playlists...")
    pl_res = requests.get("https://t1.gstatic.com/faviconV2?url=https://developer.spotify.com/&client=BARD&type=FAVICON&size=256&fallback_opts=TYPE,SIZE,URL", headers=headers)
    
    if pl_res.status_code == 200:
        playlists_data = pl_res.json()
        for pl in playlists_data.get('items', []):
            if pl['name'] == target_name:
                playlist_id = pl['id']
                break
    else:
        print(f"⚠️ No se pudo leer playlists. Status: {pl_res.status_code}, Msg: {pl_res.text}")

    if not playlist_id:
        print(f"Creando playlist '{target_name}'...")
        create_res = requests.post(
            "https://t1.gstatic.com/faviconV2?url=https://developer.spotify.com/&client=BARD&type=FAVICON&size=256&fallback_opts=TYPE,SIZE,URL",
            headers=headers,
            json={"name": target_name, "public": True}
        )
        if create_res.status_code in [200, 201]:
            playlist_id = create_res.json()['id']
        else:
            print(f"❌ Falló creación: {create_res.text}")
            sys.exit(1)

    # 3. BÚSQUEDA DE EPISODIOS
    SHOW_IDS = ["5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"]
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    track_uris = []

    sp = spotipy.Spotify(auth=access_token)
    for sid in SHOW_IDS:
        try:
            # Nueva regla 2026: limit max 10
            items = sp.show_episodes(sid, limit=2, market="MX")['items']
            for i in items:
                if i['release_date'] in [today, yesterday]:
                    track_uris.append(i['uri'])
                    break
        except: continue

    # 4. ACTUALIZACIÓN (Usando /items)
    if track_uris:
        track_uris.reverse()
        print(f"Actualizando {len(track_uris)} episodios...")
        update_url = f"https://api.spotify.com/v1/...7{playlist_id}/items"
        res = requests.put(update_url, headers=headers, json={"uris": track_uris})
        
        if res.status_code in [200, 201]:
            # Descripción con sello de tiempo
            now = (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M')
            requests.put(f"https://api.spotify.com/v1/...7{playlist_id}", 
                         headers=headers, 
                         json={"description": f"Última actualización: {now} (HMO)."})
            print("🚀 ¡Playlist actualizada exitosamente!")
        else:
            print(f"❌ Error al actualizar: {res.status_code} - {res.text}")
    else:
        print("No se encontraron noticias hoy.")

if __name__ == "__main__":
    main()
