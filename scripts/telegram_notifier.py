import requests
import logging
from pathlib import Path

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)
        
    def send(self, message):
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                },
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Error enviando a Telegram: {str(e)}")
            return False

def send_file(token, chat_id, file_path):
    """Envía archivo M3U actualizado"""
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': chat_id}
            response = requests.post(
                f"https://api.telegram.org/bot{token}/sendDocument",
                files=files,
                data=data,
                timeout=20
            )
        return response.json()
    except Exception as e:
        logging.error(f"Error enviando archivo: {str(e)}")
        return None
