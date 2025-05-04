import requests
import os
import logging
from datetime import datetime

# ========================
# 🔒 CONFIGURACIÓN (EDITAR)
# ========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7912133661:AAHXunq3ABrjYO-8ZvE5HZvDXRkuqdcooT0")  # Usar Secrets en producción
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6117213267")
PLAYLIST_NAME = "canales.m3u"
LOG_FILE = "iptv_updater.log"

# APIs (Pluto TV como ejemplo)
PLUTO_TV_API = "https://api.pluto.tv/v3/channels"
STREAM_BASE_URL = "https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/{channel_id}/master.m3u8?deviceId=web"

# ========================
# 🛠️ FUNCIONES PRINCIPALES
# ========================

def setup_logging():
    """Configura el sistema de logs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def send_telegram_alert(message: str):
    """Envía alertas a Telegram con manejo de errores."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error enviando alerta a Telegram: {str(e)}")

def check_stream(stream_url: str) -> bool:
    """Verifica si un stream está activo con timeout."""
    try:
        response = requests.head(stream_url, timeout=15, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.warning(f"Stream caído {stream_url}: {str(e)}")
        return False

def fetch_channels() -> list:
    """Obtiene canales desde la API con manejo de errores."""
    try:
        response = requests.get(PLUTO_TV_API, timeout=20)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        error_msg = f"Error al obtener canales: {str(e)}"
        logger.error(error_msg)
        send_telegram_alert(f"🚨 CRÍTICO: {error_msg}")
        return []

def generate_m3u_content(channels: list) -> tuple:
    """Genera contenido M3U y detecta enlaces rotos."""
    m3u_content = "#EXTM3U\n"
    bad_channels = []
    
    for channel in channels:
        channel_id = channel.get("_id", "")
        channel_name = channel.get("name", "Sin nombre")
        stream_url = STREAM_BASE_URL.format(channel_id=channel_id)
        
        # Añadir entrada M3U
        m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{channel_name}",{channel_name}\n'
        m3u_content += f"{stream_url}\n"
        
        # Verificar stream
        if not check_stream(stream_url):
            bad_channels.append(channel_name)
    
    return m3u_content, bad_channels

def save_playlist(content: str):
    """Guarda la playlist con timestamp."""
    try:
        with open(PLAYLIST_NAME, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Playlist guardada en {PLAYLIST_NAME}")
    except IOError as e:
        error_msg = f"Error guardando playlist: {str(e)}"
        logger.error(error_msg)
        send_telegram_alert(f"💾 ERROR: {error_msg}")

# ========================
# 🚀 EJECUCIÓN PRINCIPAL
# ========================

def main():
    start_time = datetime.now()
    logger.info("=== Iniciando actualización de playlist ===")
    
    try:
        # 1. Obtener canales
        channels = fetch_channels()
        if not channels:
            raise ValueError("No se encontraron canales")
        
        # 2. Generar M3U
        m3u_content, bad_channels = generate_m3u_content(channels)
        
        # 3. Guardar archivo
        save_playlist(m3u_content)
        
        # 4. Notificar resultados
        exec_time = (datetime.now() - start_time).total_seconds()
        status_msg = (
            f"🔄 <b>Actualización completada en {exec_time:.2f}s</b>\n"
            f"• Canales totales: {len(channels)}\n"
            f"• Enlaces rotos: {len(bad_channels)}"
        )
        
        if bad_channels:
            status_msg += "\n\n🔴 <b>Canales con problemas:</b>\n" + "\n".join(bad_channels)
        
        send_telegram_alert(status_msg)
        
    except Exception as e:
        error_msg = f"❌ ERROR GLOBAL: {str(e)}"
        logger.critical(error_msg)
        send_telegram_alert(error_msg)
    finally:
        logger.info("=== Proceso finalizado ===")

if __name__ == "__main__":
    main()
