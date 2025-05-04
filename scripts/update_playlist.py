#!/usr/bin/env python3
# 📺 IPTV M3U Playlist Updater - VERSIÓN FUNCIONAL

import requests
import os
import logging
from pathlib import Path
from datetime import datetime

# Configuración
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PLAYLIST_PATH = Path('canales.m3u')  # Se creará en la raíz del repositorio

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_pluto_channels():
    """Obtiene canales de Pluto TV API"""
    try:
        response = requests.get(
            'https://api.pluto.tv/v3/channels',
            timeout=15
        )
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        logger.error(f'Error al obtener canales: {e}')
        return []

def generate_m3u():
    """Genera archivo M3U"""
    channels = get_pluto_channels()
    if not channels:
        raise ValueError('No se obtuvieron canales')
    
    m3u_content = ['#EXTM3U']
    
    for channel in channels:
        channel_id = channel.get('_id', '')
        name = channel.get('name', 'Sin nombre')
        url = f'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/{channel_id}/master.m3u8?deviceId=web'
        
        m3u_content.append(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name}",{name}')
        m3u_content.append(url)
    
    # Guardar archivo
    with open(PLAYLIST_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    logger.info(f'Playlist generada con {len(channels)} canales')

if __name__ == '__main__':
    try:
        generate_m3u()
    except Exception as e:
        logger.error(f'Error fatal: {e}')
        exit(1)
 
