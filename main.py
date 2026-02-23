import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTH (Usando el flujo que ya sabemos que conecta)
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
    sp = spotipy.Spotify(auth=access_token)

    # 2. BÚSQUEDA DE EPISODIOS
    SHOW_IDS = ["5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"]
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

    # 3. EL BYPASS: AÑADIR A LA COLA (Player Queue)
    if track_uris:
        print(f"Añadiendo {len(track_uris)} episodios a tu cola de reproducción...")
        success_count = 0
        
        # Necesitamos que tengas Spotify abierto en algún dispositivo (celular/PC)
        for uri in track_uris:
            try:
                # Endpoint: POST /v1/me/player/queue
                # Este endpoint es más permisivo porque no modifica la base de datos de Spotify
                sp.add_to_queue(uri)
                success_count += 1
            except Exception as e:
                # Si falla es porque no hay un "dispositivo activo"
                print(f"⚠️ No se pudo añadir {uri}. Asegúrate de tener Spotify abierto.")
                break
        
        if success_count > 0:
            print(f"🚀 ¡LOGRADO! Se añadieron {success_count} episodios a tu cola.")
        else:
            print("❌ Fallo total: Abre Spotify en tu celular y vuelve a correr el script.")
    else:
        print("No se encontraron noticias.")

if __name__ == "__main__":
    main()
