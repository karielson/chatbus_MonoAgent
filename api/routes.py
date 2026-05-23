from flask import Flask, request
from config.settings import settings
from services.whatsapp import whatsapp
from agents.main import agent_executor
from models.chat_history import ChatHistory

app = Flask(__name__)
chat_history = ChatHistory()

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if token != settings.VERIFY_TOKEN:
            return 'Token inválido', 403
            
        return challenge
        
    try:
        data = request.get_json()
        
        if not data or 'entry' not in data:
            return 'EVENT_RECEIVED', 200
            
        changes = data['entry'][0].get('changes', [])
        if not changes:
            return 'EVENT_RECEIVED', 200
            
        value = changes[0].get('value', {})
        if 'messages' not in value:
            return 'EVENT_RECEIVED', 200
            
        for message in value['messages']:
            phone_number = message['from']
            msg_type = message.get('type')
            
            print(msg_type)

            try:
                # Carrega histórico atual
                history = chat_history.get_recent_history(phone_number)
                
                # Verifica o tipo de mensagem
                if msg_type == 'text':
                    # Mensagem de texto
                    user_message = message['text']['body']
                    
                    # Adiciona texto ao histórico
                    chat_history.add_message(phone_number, "human", user_message)
                    
                    # Processa com o agente
                    response = agent_executor.invoke({
                        "input": user_message,
                        "chat_history": history
                    })
                    
                    # Adiciona resposta ao histórico
                    chat_history.add_message(phone_number, "system", response['output'])
                    
                    # Envia resposta
                    whatsapp.send_message(phone_number, response['output'])
                    
                elif msg_type == 'location':
                    # Mensagem de localização
                    user_lat = message['location']['latitude']
                    user_lng = message['location']['longitude']
                    
                    # Armazena localização no histórico (ou em outro local, se preferir)
                    chat_history.add_message(phone_number, "human", f"{user_lat},{user_lng}")
                    
                    response = agent_executor.invoke({
                        "input": f"{user_lat},{user_lng}",
                        "chat_history": history
                    })

                    chat_history.add_message(phone_number, "system", response['output'])

                    # Envie uma resposta confirmando o recebimento da localização
                    # e solicitando o destino se ainda não estiver claro no histórico
                    whatsapp.send_message(phone_number, response['output'])
                
                else:
                    # Tipos que não estamos tratando (áudio, imagem etc.)
                    # Poderia adicionar lógica extra se desejado
                    whatsapp.send_message(
                        phone_number,
                        "Não entendi, por favor envie um texto ou sua localização. 🙏"
                    )
            
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                error_msg = (
                    "Desculpe, tive um problema ao processar sua mensagem. "
                    "Por favor, tente novamente."
                )
                whatsapp.send_message(phone_number, error_msg)
        
        return 'EVENT_RECEIVED', 200
        
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return 'ERROR', 500


@app.route("/")
def home():
    return "Servidor de Transporte Público - Status: Online"
