from flask import Flask
from pyngrok import ngrok
from api.routes import app as api_app
from config.settings import settings

def setup_ngrok():
    """Configura o túnel ngrok para desenvolvimento."""
    if settings.NGROK_AUTHTOKEN:
        ngrok.set_auth_token(settings.NGROK_AUTHTOKEN)
        public_url = ngrok.connect(5000)
        print(f"Servidor público em: {public_url}")
    else:
        print("Token do ngrok não configurado!")

if __name__ == '__main__':
    # Configura ngrok em ambiente de desenvolvimento
    if not settings.WHATSAPP_TOKEN.startswith('prod_'):
        setup_ngrok()
    
    # Inicia o servidor Flask
    api_app.run(port=5000)