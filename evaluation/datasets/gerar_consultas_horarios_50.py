# evaluation/datasets/gerar_consultas_horarios_50.py

from __future__ import annotations

import csv
from pathlib import Path

from services.sptrans import sptrans
from scrapers.horarios import horarios_scraper


OUTPUT_PATH = Path("evaluation/datasets/consultas_horarios_50.csv")


DIAS = {
    "0": "dia útil",
    "1": "sábado",
    "2": "domingo",
}


CANDIDATAS = [
    "6455-10",
    "875A-10",
    "8000-10",
    "715M-10",
    "809U-10",
    "709M-10",
    "857R-10",
    "875C-10",
    "675K-10",
    "675X-10",
    "669A-10",
    "637A-10",
    "637G-10",
    "637J-10",
    "6450-10",
    "6451-10",
    "6500-10",
    "6505-10",
    "695T-10",
    "6960-10",
    "695Y-10",
    "6913-10",
    "6913-21",
    "701U-10",
    "702U-10",
    "702C-10",
    "701A-10",
    "7016-10",
    "7245-10",
    "7281-10",
    "7267-10",
    "775A-10",
    "775F-10",
    "775P-10",
    "778R-10",
    "778J-10",
    "778P-10",
    "8001-10",
    "8002-10",
    "8003-10",
    "8012-10",
    "8018-10",
    "8020-10",
    "8050-10",
    "8075-10",
    "807A-10",
    "809L-10",
    "8319-10",
    "847J-10",
    "8538-10",
    "857A-10",
    "8610-10",
    "8615-10",
    "8686-10",
    "875H-10",
]


MODELOS_PERGUNTA = [
    "Quais os horários da linha {linha} no {dia_texto}?",
    "Me informe a tabela de horários da linha {linha} no {dia_texto}.",
    "Qual é o quadro de horários da linha {linha} no {dia_texto}?",
    "Preciso dos horários da linha {linha} no {dia_texto}.",
    "A linha {linha} tem quais horários no {dia_texto}?",
]


def resolver_linha_exata(linha: str) -> str | None:
    """
    Verifica se a linha existe na SPTrans e retorna o letreiro resolvido.
    """
    linhas = sptrans.buscar_linha(linha)

    if not linhas:
        return None

    linhas_exatas = [
        item for item in linhas
        if str(item).strip().lower() == linha.strip().lower()
    ]

    if linhas_exatas:
        return linhas_exatas[0]

    if len(linhas) == 1:
        return linhas[0]

    return None


def linha_opera_no_dia(linha_resolvida: str, dia_operacional: str) -> bool:
    """
    Verifica se há horários oficiais para a linha no dia operacional.
    """
    horarios = horarios_scraper.scrape(linha_resolvida, dia_operacional)
    return bool(horarios)


def gerar_consultas() -> list[dict]:
    consultas = []
    contador = 1

    for linha in CANDIDATAS:
        print(f"Verificando linha {linha}...")

        linha_resolvida = resolver_linha_exata(linha)

        if not linha_resolvida:
            print(f"  Ignorada: linha não encontrada ou ambígua.")
            continue

        for dia_operacional, dia_texto in DIAS.items():
            print(f"  Testando {linha_resolvida} - {dia_texto}...")

            if not linha_opera_no_dia(linha_resolvida, dia_operacional):
                print(f"    Não opera ou sem horários encontrados.")
                continue

            modelo = MODELOS_PERGUNTA[(contador - 1) % len(MODELOS_PERGUNTA)]
            pergunta = modelo.format(
                linha=linha_resolvida,
                dia_texto=dia_texto,
            )

            consultas.append({
                "id_consulta": f"H{contador:03d}",
                "tipo_tarefa": "horarios",
                "pergunta": pergunta,
                "linha": linha_resolvida,
                "origem": "",
                "destino": "",
                "parada": "",
                "sentido": "",
                "dia_operacional": dia_operacional,
                "preferencia": "",
                "ferramenta_esperada": "consultar_horarios",
                "faq_pergunta_referencia": "",
                "faq_resposta_referencia": "",
                "faq_categoria": "",
            })

            print(f"    Incluída: {pergunta}")
            contador += 1

            if len(consultas) >= 50:
                return consultas

    return consultas


def salvar_csv(consultas: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not consultas:
        raise ValueError("Nenhuma consulta válida foi gerada.")

    fieldnames = list(consultas[0].keys())

    with open(OUTPUT_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(consultas)


def main():
    consultas = gerar_consultas()
    salvar_csv(consultas)

    print("=" * 70)
    print(f"Consultas válidas geradas: {len(consultas)}")
    print(f"Arquivo salvo em: {OUTPUT_PATH}")
    print("=" * 70)

    if len(consultas) < 50:
        print(
            "Atenção: foram geradas menos de 50 consultas. "
            "Adicione mais linhas candidatas à lista CANDIDATAS."
        )


if __name__ == "__main__":
    main()