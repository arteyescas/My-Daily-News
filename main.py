import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTH (Usamos /me/ para evitar errores de ID)
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
    
    # 2. BUSCAR O CREAR PLAYLIST (Nuevo Endpoint /me/playlists)
    target_name = "Daily News Summary"
    playlist_id = None
    
    # Obtener mis playlists (Endpoint /me/playlists)
    me_playlists = requests.get("https://t1.gstatic.com/faviconV2?url=https://developer.spotify.com/&client=BARD&type=FAVICON&size=256&fallback_opts=TYPE,SIZE,URL", headers=headers).json()
    for pl in me_playlists.get('items', []):
        if pl['name'] == target_name:
            playlist_id = pl['id']
            break

    if not playlist_id:
        print("Migración 2026: Creando playlist vía /me/playlists...")
        create_res = requests.post(
            "https://t1.gstatic.com/faviconV2?url=https://developer.spotify.com/&client=BARD&type=FAVICON&size=256&fallback_opts=TYPE,SIZE,URL",
            headers=headers,
            json={"name": target_name, "public": True}
        )
        playlist_id = create_res.json()['id']

    # 3. BUSCAR PODCASTS (Lógica de fecha intacta)
    SHOW_IDS = ["5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"]
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    track_uris = []

    sp = spotipy.Spotify(auth=access_token)
    for sid in SHOW_IDS:
        try:
            # Nota: limit=2 cumple con el nuevo máximo de 10
            items = sp.show_episodes(sid, limit=2, market="MX")['items']
            for i in items:
                if i['release_date'] in [today, yesterday]:
                    track_uris.append(i['uri'])
                    break
        except: continue

    # 4. ACTUALIZAR PLAYLIST (Nuevo Endpoint /items)
    if track_uris:
        track_uris.reverse()
        print(f"Migración 2026: Actualizando vía /playlists/{playlist_id}/items")
        
        # IMPORTANTE: La doc dice que PUT /tracks ahora es PUT /items
        update_url = f"https://api.spotify.com/v1/...7{playlist_id}/items"
        res = requests.put(update_url, headers=headers, json={"uris": track_uris})
        
        if res.status_code in [200, 201]:
            print("🚀 ¡LOGRADO! Tu playlist de noticias está lista.")
        else:
            print(f"❌ Error Migración: {res.status_code} - {res.text}")
    else:
        print("No hay noticias nuevas para hoy.")

if __name__ == "__main__":
    main()
