import requests
import os

# Función para obtener canales de Pluto TV
def get_pluto_channels():
    url = "https://api.pluto.tv/v3/channels"
    response = requests.get(url)
    data = response.json()
    return data["data"]

# Generar lista M3U
def generate_m3u():
    channels = get_pluto_channels()
    m3u_content = "#EXTM3U\n"
    
    for channel in channels:
        m3u_content += f'#EXTINF:-1 tvg-id="{channel["_id"]}" tvg-name="{channel["name"]}",{channel["name"]}\n'
        m3u_content += f'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/{channel["_id"]}/master.m3u8?deviceId=web\n'
    
    return m3u_content

# Guardar en archivo
with open("../canales.m3u", "w") as file:
    file.write(generate_m3u())

print("✅ Lista M3U actualizada")
