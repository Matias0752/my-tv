#!/usr/bin/env python3
import os
import shutil
import logging
import requests
from pathlib import Path
from datetime import datetime
from scripts.telegram_notifier import TelegramNotifier, send_file

# Configuración
CONFIG = {
    'source_dir': Path("mis_canales"),
    'output_file': Path("canales_chile.m3u"),
    'telegram': {
        'token': os.environ.get("TELEGRAM_TOKEN"),
        'chat_id': os.environ.get("TELEGRAM_CHAT_ID")
    }
}

def setup():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("m3u_updater.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_latest_m3u(source_dir):
    m3u_files = list(source_dir.glob("*.m3u*"))
    if not m3u_files:
        raise FileNotFoundError(f"No se encontraron archivos .m3u en {source_dir}")
    return max(m3u_files, key=lambda f: f.stat().st_mtime)

def generate_report(input_file, output_file):
    with open(input_file) as f:
        line_count = sum(1 for line in f if line.strip())

    return f"""📡 <b>Actualización Lista IPTV</b>

📅 <i>{datetime.now().strftime('%d/%m/%Y %H:%M')}</i>
📂 <b>Archivo fuente:</b> {input_file.name}
📝 <b>Canales totales:</b> {line_count//2}
📦 <b>Tamaño generado:</b> {output_file.stat().st_size/1024:.1f} KB"""

def verificar_links(file_path, notifier):
    errores = []
    with open(file_path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line.startswith("http"):
                try:
                    response = requests.head(line, timeout=5)
                    if response.status_code >= 400:
                        errores.append((i, line, response.status_code))
                        logging.warning(f"Canal {i} ({line}) no disponible: {response.status_code}")
                except Exception as e:
                    errores.append((i, line, str(e)))
                    logging.warning(f"Canal {i} ({line}) no disponible: {str(e)}")

    if errores:
        mensaje = "<b>⚠️ Links M3U con error:</b>\n\n"
        for i, url, error in errores[:10]:
            mensaje += f"{i}. <code>{url}</code>\n└ Error: {error}\n\n"
        if len(errores) > 10:
            mensaje += f"... y {len(errores) - 10} más."
        notifier.send(mensaje)

def main():
    logger = setup()
    notifier = TelegramNotifier(CONFIG['telegram']['token'], CONFIG['telegram']['chat_id'])

    try:
        logger.info("=== INICIANDO ACTUALIZACIÓN ===")
        latest_m3u = get_latest_m3u(CONFIG['source_dir'])

        shutil.copy2(latest_m3u, CONFIG['output_file'])
        logger.info(f"Archivo copiado: {latest_m3u} → {CONFIG['output_file']}")

        verificar_links(CONFIG['output_file'], notifier)

        report = generate_report(latest_m3u, CONFIG['output_file'])
        logger.info(report)

        notifier.send(report)
        send_file(
            CONFIG['telegram']['token'],
            CONFIG['telegram']['chat_id'],
            CONFIG['output_file']
        )

    except Exception as e:
        error_msg = f"❌ <b>ERROR:</b> {str(e)}"
        logger.error(error_msg)
        notifier.send(error_msg)
        raise

if __name__ == "__main__":
    main()
