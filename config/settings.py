import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys e Tokens
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    NGROK_AUTHTOKEN = os.getenv('NGROK_AUTHTOKEN')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    SPTRANS_API_TOKEN = os.getenv('SPTRANS_API_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Configurações do Banco de Dados
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chat_history.db')
    
    # Configurações de Cache
    CACHE_EXPIRE_HOURS = 24
    
    # Configurações da API
    API_BASE_URL = 'https://api.olhovivo.sptrans.com.br/v2.1'
    MAPS_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
    WHATSAPP_API_URL = 'https://graph.facebook.com/v21.0/458777567322293/messages'

settings = Settings()