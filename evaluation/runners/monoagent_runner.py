# evaluation/runners/monoagent_runner.py

from __future__ import annotations

import time
import traceback
from datetime import datetime

from evaluation.runners.base_runner import BaseRunner, ModelRunResult
from agents.main import agent_executor_eval


TOOL_NAME_MAP = {
    "quadro_de_horario_tool": "consultar_horarios",
    "rota_tool": "consultar_rota",
    "faq_tool": "faq",
    "status_onibus_tool": "status_onibus_tool",
    "previsao_chegada_tool": "consultar_previsao_chegada",
}


def _extract_tool_used(result: dict) -> str | None:
    """
    Extrai a ferramenta principal usada pelo AgentExecutor do LangChain.

    Ignora sugestoes_contextuais_tool, pois ela é uma ferramenta complementar
    e não deve contar para PEF.
    """
    steps = result.get("intermediate_steps") or []

    tools_usadas = []

    for step in steps:
        try:
            action = step[0]
            tool_name = getattr(action, "tool", None)

            if not tool_name:
                continue

            if tool_name == "sugestoes_contextuais_tool":
                continue

            tools_usadas.append(tool_name)

        except Exception:
            continue

    if not tools_usadas:
        return None

    # Usa a primeira ferramenta principal acionada.
    raw_tool = tools_usadas[0]

    return TOOL_NAME_MAP.get(raw_tool, raw_tool)


class MonoAgentRunner(BaseRunner):
    """
    Executor experimental da arquitetura monoagente LangChain.
    """

    arquitetura = "monoagente"

    def run(self, row: dict) -> ModelRunResult:
        id_consulta = str(row.get("id_consulta", "")).strip()
        tipo_tarefa = str(row.get("tipo_tarefa", "")).strip()
        pergunta = str(row.get("pergunta", "")).strip()
        ferramenta_esperada = str(row.get("ferramenta_esperada", "")).strip() or None

        inicio = datetime.now()
        t0 = time.perf_counter()

        erro = None
        resposta = ""
        ferramenta_usada = None

        try:
            result = agent_executor_eval.invoke({
                "input": pergunta,
                "chat_history": [],
            })

            resposta = str(result.get("output", "")).strip()
            ferramenta_usada = _extract_tool_used(result)

            if not resposta:
                resposta = "Não obtive resposta do monoagente."

        except Exception as e:
            resposta = ""
            erro = f"{type(e).__name__}: {str(e)}"
            traceback.print_exc()

        t1 = time.perf_counter()
        fim = datetime.now()

        return ModelRunResult(
            id_consulta=id_consulta,
            tipo_tarefa=tipo_tarefa,
            pergunta=pergunta,
            resposta=resposta,
            arquitetura=self.arquitetura,
            tempo_resposta_seg=round(t1 - t0, 4),
            ferramenta_esperada=ferramenta_esperada,
            ferramenta_usada=ferramenta_usada,
            erro=erro,
            timestamp_inicio=inicio.isoformat(),
            timestamp_fim=fim.isoformat(),
        )