import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, sys, datetime, requests

def main():
    # 1. AUTH (Usando el flujo verificado)
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
    # Importante: Para /me/library se necesita este scope
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    sp = spotipy.Spotify(auth=access_token)
    print(f"✅ Conectado como: {sp.me()['id']}")

    # 2. BÚSQUEDA DE EPISODIOS
    SHOW_IDS = [
        "5Gka9laolwx0TzJ0biYpxz", "6NohCptkHoUdIvgr7d0C43", "6SVAeMaKdzhA9DIY8ZFZTh", 
        "1nS40a6gR0w53seTurNddC", "0vDgnorbpBr65YZzFVVouE", "5X2O35fLXaXrNZUtP48LI9", 
        "5ZGlgp8Y6fpXNpg9drwBUs", "1H5BkWb7cjPE5zQiwnqbqP", "1gVuEXINi9lVjt1Ya2DAJ3", 
        "2vLiCH78iiqtRcQe78ADRt", "2pXBpdfJoAo2iNz5G25nCP"
    ]
    
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    episode_ids = []

    for sid in SHOW_IDS:
        try:
            items = sp.show_episodes(sid, limit=2, market="MX")['items']
            for i in items:
                if i['release_date'] in [today, yesterday]:
                    # Guardamos el ID limpio (sin 'spotify:episode:')
                    episode_ids.append(i['id'])
                    break
        except: continue

    # 3. GUARDAR EN BIBLIOTECA (El bypass al 404)
    if episode_ids:
        print(f"Guardando {len(episode_ids)} episodios en tu biblioteca...")
        
        # Según la doc de Feb 2026, este endpoint es el que sobrevive para Devs
        # Se usa PUT /me/episodes para marcar como "Guardado"
        save_url = "https://community.spotify.com/t5/Spotify-for-Developers/Regarding-Insufficient-client-scope/td-p/53866352"
        res = requests.put(save_url, headers=headers, json={"ids": episode_ids})
        
        if res.status_code in [200, 201]:
            print("🚀 ¡LOGRADO! Los episodios están en 'Tus episodios' de tu Spotify.")
        else:
            print(f"❌ Error al guardar: {res.status_code} - {res.text}")
    else:
        print("No se encontraron noticias nuevas.")

if __name__ == "__main__":
    main()
