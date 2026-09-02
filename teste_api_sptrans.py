from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

SPTRANS_TOKEN = os.getenv("SPTRANS_API_TOKEN") or os.getenv("SPTRANS_API_KEY")

BASE_URL = "https://api.olhovivo.sptrans.com.br/v2.1"


def print_bloco(titulo):
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)


def testar_login(session):
    print_bloco("1. TESTE DE LOGIN NA API SPTRANS")

    if not SPTRANS_TOKEN:
        print("ERRO: token não encontrado no .env")
        print("Verifique se existe SPTRANS_TOKEN=... ou SPTRANS_API_KEY=...")
        return False

    url = f"{BASE_URL}/Login/Autenticar"
    params = {"token": SPTRANS_TOKEN}

    try:
        response = session.post(url, params=params, timeout=20)

        print("URL:", response.url)
        print("Status code:", response.status_code)
        print("Resposta bruta:", response.text)
        print("Cookies:", session.cookies.get_dict())

        if response.status_code != 200:
            print("ERRO: API respondeu status diferente de 200.")
            return False

        autenticado = response.text.strip().lower() == "true"

        if not autenticado:
            print("ERRO: Login retornou false. Token inválido ou API recusou autenticação.")
            return False

        print("OK: Login autenticado com sucesso.")
        return True

    except Exception as e:
        print("ERRO no login:", repr(e))
        return False


def testar_busca_linha(session, termo):
    print_bloco(f"2. TESTE DE BUSCA DE LINHA: {termo}")

    url = f"{BASE_URL}/Linha/Buscar"
    params = {"termosBusca": termo}

    try:
        response = session.get(url, params=params, timeout=20)

        print("URL:", response.url)
        print("Status code:", response.status_code)
        print("Resposta bruta:", response.text[:2000])

        if response.status_code != 200:
            print("ERRO: busca de linha retornou status diferente de 200.")
            return None

        try:
            dados = response.json()
        except Exception:
            print("ERRO: resposta não veio em JSON.")
            return None

        print("Quantidade de linhas encontradas:", len(dados))

        if dados:
            print("\nPrimeiros resultados:")
            for item in dados[:10]:
                print(json.dumps(item, ensure_ascii=False, indent=2))

        return dados

    except Exception as e:
        print("ERRO na busca de linha:", repr(e))
        return None


def testar_posicao_linha(session, codigo_linha):
    print_bloco(f"3. TESTE DE POSIÇÃO DA LINHA CÓDIGO cl={codigo_linha}")

    url = f"{BASE_URL}/Posicao/Linha"
    params = {"codigoLinha": codigo_linha}

    try:
        response = session.get(url, params=params, timeout=20)

        print("URL:", response.url)
        print("Status code:", response.status_code)
        print("Resposta bruta:", response.text[:2000])

        if response.status_code != 200:
            print("ERRO: posição retornou status diferente de 200.")
            return None

        try:
            dados = response.json()
        except Exception:
            print("ERRO: resposta não veio em JSON.")
            return None

        print(json.dumps(dados, ensure_ascii=False, indent=2)[:3000])
        return dados

    except Exception as e:
        print("ERRO na posição:", repr(e))
        return None


def main():
    session = requests.Session()

    login_ok = testar_login(session)

    if not login_ok:
        print("\nRESULTADO FINAL: falha no login/autenticação da API.")
        return

    termos_teste = [
        "6455-10",
        "6455",
        "875A-10",
        "875A",
        "8000",
    ]

    resultados = {}

    for termo in termos_teste:
        dados = testar_busca_linha(session, termo)
        resultados[termo] = dados

    print_bloco("4. ANÁLISE DOS RESULTADOS")

    for termo, dados in resultados.items():
        if dados is None:
            print(f"{termo}: ERRO na requisição")
        elif len(dados) == 0:
            print(f"{termo}: API respondeu, mas não encontrou linhas")
        else:
            print(f"{termo}: encontrou {len(dados)} linha(s)")

    # Testa posição usando o primeiro código interno encontrado
    for termo, dados in resultados.items():
        if dados:
            primeira_linha = dados[0]
            codigo_linha = primeira_linha.get("cl")

            print_bloco("5. PRIMEIRA LINHA VÁLIDA ENCONTRADA")
            print("Termo:", termo)
            print(json.dumps(primeira_linha, ensure_ascii=False, indent=2))

            if codigo_linha:
                testar_posicao_linha(session, codigo_linha)
            else:
                print("ERRO: campo 'cl' não encontrado na linha.")
            break

    print_bloco("FIM DO TESTE")


if __name__ == "__main__":
    main()