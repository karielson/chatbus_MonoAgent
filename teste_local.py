from langchain_core.messages import HumanMessage, SystemMessage
from agents.main import agent_executor  # Importando o executor diretamente
from datetime import datetime
import sys
import traceback

def format_agent_response(response):
    """Formata a resposta do agente para melhor legibilidade."""
    separator = "-" * 50
    return f"\n{separator}\nResposta: {response}\n{separator}\n"

def save_conversation(chat_history):
    """Salva o histórico da conversa em um arquivo."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversa_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Histórico da Conversa\n")
        f.write("=" * 50 + "\n\n")
        
        for msg in chat_history:
            role = "Usuário" if isinstance(msg, HumanMessage) else "Agente"
            f.write(f"{role}: {msg.content}\n\n")
    
    return filename

def main():
    print("\n=== Chatbot de Transporte Público - Modo Teste ===")
    print("Digite 'sair', 'exit' ou 'quit' para encerrar")
    print("Digite 'salvar' para salvar o histórico da conversa")
    print("=" * 50 + "\n")
    
    chat_history = []
    
    while True:
        try:
            # Input do usuário
            user_question = input("\nVocê: ").strip()
            
            # Comandos especiais
            if user_question.lower() in ["sair", "exit", "quit"]:
                if chat_history:
                    save = input("\nDeseja salvar a conversa? (s/n): ").lower()
                    if save == 's':
                        filename = save_conversation(chat_history)
                        print(f"\nConversa salva em: {filename}")
                print("\nEncerrando a conversa. Até logo!")
                break
                
            elif user_question.lower() == "salvar":
                filename = save_conversation(chat_history)
                print(f"\nConversa salva em: {filename}")
                continue
                
            elif not user_question:
                print("Por favor, digite sua pergunta.")
                continue
            
            # Adiciona a pergunta ao histórico
            chat_history.append(HumanMessage(content=user_question))
            
            # Processa a mensagem com o agente
            result = agent_executor.invoke({
                "input": user_question,
                "chat_history": chat_history
            })
            
            # Formata e mostra a resposta
            response = result['output']
            print(format_agent_response(response))
            
            # Adiciona a resposta ao histórico
            chat_history.append(SystemMessage(content=response))
            
        except KeyboardInterrupt:
            print("\n\nOperação interrompida pelo usuário.")
            sys.exit(0)
            
        except Exception as e:
            print(f"\nErro ao processar a mensagem:")
            print(f"Tipo do erro: {type(e).__name__}")
            print(f"Descrição: {str(e)}")
            print("\nDetalhes técnicos:")
            traceback.print_exc()
            print("\nPor favor, tente novamente.")

if __name__ == "__main__":
    main()