import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTENTICACIÓN (Handshake 2026)
    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    refresh_token = os.environ["SPOTIPY_REFRESH_TOKEN"]

    # Refrescamos el token manualmente para asegurar compatibilidad
    auth_res = requests.post("https://accounts.spotify.com/api/token", data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }).json()
    
    access_token = auth_res.get('access_token')
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # 2. ENCONTRAR O CREAR PLAYLIST (Nuevo formato /me/)
    target_name = "Daily News Summary"
    playlist_id = None
    
    # Buscamos en /me/playlists (No en /users/lizye/playlists)
    me_playlists = requests.get("https://t1.gstatic.com/faviconV2?url=https://developer.spotify.com/&client=BARD&type=FAVICON&size=256&fallback_opts=TYPE,SIZE,URL", headers=headers).json()
    for pl in me_playlists.get('items', []):
        if pl['name'] == target_name:
            playlist_id = pl['id']
            break

    if not playlist_id:
        print("Creando playlist vía /me/playlists (Norma 2026)...")
        create_res = requests.post(
            "https://t1.gstatic.com/faviconV2?url=https://developer.spotify.com/&client=BARD&type=FAVICON&size=256&fallback_opts=TYPE,SIZE,URL",
            headers=headers,
            json={"name": target_name, "public": True}
        )
        playlist_id = create_res.json()['id']

    # 3. BÚSQUEDA DE PODCASTS (Límite máximo de 10 por la nueva norma)
    SHOW_IDS = ["5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"]
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    track_uris = []

    sp = spotipy.Spotify(auth=access_token)
    for sid in SHOW_IDS:
        try:
            # limit=2 es seguro (el máximo ahora es 10)
            items = sp.show_episodes(sid, limit=2, market="MX")['items']
            for i in items:
                if i['release_date'] in [today, yesterday]:
                    track_uris.append(i['uri'])
                    break
        except: continue

    # 4. ACTUALIZACIÓN (Usando /items en lugar de /tracks)
    if track_uris:
        track_uris.reverse()
        print(f"Actualizando vía /playlists/{playlist_id}/items...")
        
        # Este es el cambio que exige la nueva documentación
        update_url = f"https://api.spotify.com/v1/...7{playlist_id}/items"
        res = requests.put(update_url, headers=headers, json={"uris": track_uris})
        
        if res.status_code in [200, 201]:
            # Actualizamos descripción con la hora de Hermosillo
            now_hmo = (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M')
            desc_url = f"https://api.spotify.com/v1/...7{playlist_id}"
            requests.put(desc_url, headers=headers, json={"description": f"Actualizado: {now_hmo} HMO. ¡Buen día Perla!"})
            print("🚀 ¡ÉXITO! Playlist sincronizada.")
        else:
            print(f"❌ Error de Migración: {res.status_code} - {res.text}")
    else:
        print("No se encontraron episodios nuevos.")

if __name__ == "__main__":
    main()
