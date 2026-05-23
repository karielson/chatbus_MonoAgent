import requests
from config.settings import settings
from typing import Dict, Any

class WhatsAppService:
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.token = settings.WHATSAPP_TOKEN

    def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': phone_number,
            'text': {'body': message}
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

whatsapp = WhatsAppService()

