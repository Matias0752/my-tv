#!/usr/bin/env python3
import shutil
import logging
from pathlib import Path
from datetime import datetime
from .telegram_notifier import TelegramNotifier, send_file

# Configuración
CONFIG = {
    'source_dir': Path("mis_canales"),
    'output_file': Path("canales_chile.m3u"),
    'telegram': {
        'token': "TU_TOKEN_BOT",  # Reemplázalo
        'chat_id': "TU_CHAT_ID"   # Reemplázalo
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

def main():
    logger = setup()
    notifier = TelegramNotifier(CONFIG['telegram']['token'], CONFIG['telegram']['chat_id'])
    
    try:
        logger.info("=== INICIANDO ACTUALIZACIÓN ===")
        latest_m3u = get_latest_m3u(CONFIG['source_dir'])
        
        # Copiar archivo
        shutil.copy2(latest_m3u, CONFIG['output_file'])
        logger.info(f"Archivo copiado: {latest_m3u} → {CONFIG['output_file']}")
        
        # Generar reporte
        report = generate_report(latest_m3u, CONFIG['output_file'])
        logger.info(report)
        
        # Notificar
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
