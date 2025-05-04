#!/usr/bin/env python3
# 📺 Lista M3U para Canales Chilenos - IPTV

import requests
import os
import logging
from pathlib import Path

# Configuración
PLAYLIST_PATH = Path('canales_chile.m3u')
CHILE_SOURCES = [
    "https://raw.githubusercontent.com/ivantapia882/Free_M3U/main/M3U/Chile.m3u",
    "https://iptv-org.github.io/iptv/countries/cl.m3u",
    "https://raw.githubusercontent.com/ruvelro/TV-Online/master/M3U/Chile.m3u"
]

# Canales manuales de respaldo (ejemplos)
BACKUP_CHANNELS = """
#EXTM3U
#EXTINF:-1 tvg-id="TVN" tvg-name="TVN" tvg-logo="https://i.imgur.com/xyz123.png",TVN
https://univision-ott-live.akamaized.net/tvn_hls/chunklist.m3u8
#EXTINF:-1 tvg-id="Mega" tvg-name="Mega" tvg-logo="https://i.imgur.com/abc456.png",Mega
https://mdstrm.com/live-stream-playlist/5a7b1e63a8da282c34d65445.m3u8
#EXTINF:-1 tvg-id="Chilevision" tvg-name="Chilevisión",Chilevisión
https://live.chilevision.cl/stream/stream.m3u8
"""

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

def fetch_chile_playlist():
    """Obtiene listas M3U de fuentes chilenas"""
    for source in CHILE_SOURCES:
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            
            # Filtra solo canales chilenos (por si la lista es mixta)
            content = "\n".join(
                line for line in response.text.split('\n') 
                if 'tvg-country="CL"' in line or 'tvg-id="CL_' in line or not line.startswith('#EXT')
            )
            
            return content or response.text  # Devuelve filtrado o original
            
        except Exception as e:
            logger.warning(f"Fuente {source} falló: {str(e)}")
    return None

def save_playlist(content):
    """Guarda la playlist con validación"""
    try:
        with open(PLAYLIST_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verificación
        line_count = len(content.split('\n'))
        logger.info(f"Playlist guardada con {line_count} líneas")
        return True
        
    except Exception as e:
        logger.error(f"Error guardando playlist: {str(e)}")
        return False

if __name__ == '__main__':
    logger.info("=== Obteniendo canales chilenos ===")
    
    # 1. Intenta con fuentes en línea
    playlist = fetch_chile_playlist()
    
    # 2. Si falla, usa canales de respaldo
    if not playlist:
        logger.warning("Usando lista de respaldo")
        playlist = BACKUP_CHANNELS
    
    # 3. Guarda y verifica
    if save_playlist(playlist):
        logger.info("✅ Proceso completado")
        exit(0)
    else:
        logger.error("❌ Fallo crítico")
        exit(1)
