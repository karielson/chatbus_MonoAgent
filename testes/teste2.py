from langchain_core.messages import HumanMessage, SystemMessage
from agente import agent_main  # Substitua pelo módulo correto

if __name__ == "__main__":

 
    # Inicializando o histórico de mensagens
    chat_history = []

        # Loop para manter a conversa contínua
    while True:
        user_question = input("Você: ")  # Input do usuário
        
        # Permitir ao usuário encerrar a conversa
        if user_question.lower() in ["sair", "exit", "quit"]:
            print("Encerrando a conversa. Até logo!")
            break

       
            
        # Adiciona a pergunta do usuário ao histórico
        chat_history.append(HumanMessage(content=user_question))
        result = agent_main(user_question, chat_history)

        # Mostra a resposta do agente
        print(f"Agente: {result}")
        
        # Adiciona a resposta do agente ao histórico
        chat_history.append(SystemMessage(content=result))