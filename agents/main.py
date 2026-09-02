from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from config.settings import settings
from .tools import (
    quadro_de_horario_tool,
    rota_tool,
    faq_tool,
    status_onibus_tool,
    previsao_chegada_tool,
    sugestoes_contextuais_tool,
)


def create_agent(include_suggestions: bool = True):
    """Cria e configura o agente de chat."""

    tools = [
        quadro_de_horario_tool,
        rota_tool,
        faq_tool,
        status_onibus_tool,
        previsao_chegada_tool,
    ]

    if include_suggestions:
        tools.append(sugestoes_contextuais_tool)

    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model_name="gpt-4o-mini",
        temperature=0,
    )

    if include_suggestions:
        suggestion_instruction =        """
        Use a ferramenta `sugestoes_contextuais_tool` apenas se isso realmente agregar valor.
        Nunca substitua a resposta principal pelas sugestões.
        """
        #Após responder a dúvida do usuário, você pode sugerir até 2 funcionalidades complementares úteis.
    else:
        suggestion_instruction = """
        Não gere sugestões complementares. Responda apenas à pergunta principal do usuário usando a ferramenta adequada.
        """

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
        Você é um assistente especializado no transporte público de São Paulo.

        Use as ferramentas de acordo com a necessidade:
        - faq_tool: Para responder perguntas gerais sobre o sistema.
        - quadro_de_horario_tool: Para consultar horários específicos de linhas.
        - rota_tool: Para fornecer informações sobre trajetos.
        - status_onibus_tool: Para gerar o link do Olho Vivo com o mapa da linha de ônibus.
        - previsao_chegada_tool: Para informar o tempo de chegada do próximo ônibus em uma parada.

        Regras:
        1. Responda de forma clara, objetiva e amigável.
        2. Use apenas dados retornados pelas ferramentas.
        3. Não invente informações.
        4. Se não encontrar a informação, diga que não encontrou.
        5. A resposta principal deve conter o resultado da ferramenta adequada.

        {suggestion_instruction}
        """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


# Executor normal da aplicação
agent_executor = create_agent(include_suggestions=True)

# Executor específico para avaliação
agent_executor_eval = create_agent(include_suggestions=False)