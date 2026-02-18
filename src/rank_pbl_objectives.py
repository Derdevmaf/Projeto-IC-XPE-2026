import os
import glob
import time
import csv
import json
from dotenv import load_dotenv
from google import genai

# ==========================================================
# 🔐 Carregar .env
# ==========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY não encontrada no .env")

client = genai.Client(
    api_key=api_key,
    http_options={"api_version": "v1"}
)

# ==========================================================
# ⚙ Configuração
# ==========================================================

K = 5  # Top K PBLs por objetivo
SLEEP_SECONDS = 3  # Delay para evitar rate limit

# ==========================================================
# 📁 Diretórios
# ==========================================================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)

# ==========================================================
# 📚 Funções Auxiliares
# ==========================================================

def carregar_objetivos_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, list):
        raise ValueError(f"❌ Estrutura inesperada em {caminho} (esperado lista)")

    objetivos = []

    for item in dados:
        if "objetivo_de_aprendizagem" not in item:
            raise KeyError(
                f"❌ Campo 'objetivo_de_aprendizagem' não encontrado.\n"
                f"Campos disponíveis: {list(item.keys())}"
            )
        objetivos.append(item["objetivo_de_aprendizagem"])

    return objetivos


def carregar_projetos_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, list):
        raise ValueError(f"❌ Estrutura inesperada em {caminho} (esperado lista)")

    projetos = []

    for item in dados:
        if "nome_do_projeto" not in item:
            raise KeyError(
                f"❌ Campo 'nome_do_projeto' não encontrado.\n"
                f"Campos disponíveis: {list(item.keys())}"
            )
        projetos.append(item["nome_do_projeto"])

    return projetos


def extrair_identificador(caminho_completo, prefixo):
    nome_base = os.path.basename(caminho_completo)
    nome_sem_prefixo = nome_base.replace(prefixo, "")
    nome_sem_extensao = os.path.splitext(nome_sem_prefixo)[0]
    return nome_sem_extensao


def chamar_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"❌ Erro ao chamar Gemini: {e}")
        return None
    
    


# ==========================================================
# 🔎 Buscar arquivos JSON
# ==========================================================

arquivos_objetivos = glob.glob(
    os.path.join(DATA_RAW_DIR, "projetos_objetivos_*.json")
)

arquivos_pbl = glob.glob(
    os.path.join(DATA_RAW_DIR, "projetos_pbl_*.json")
)

mapa_objetivos = {
    extrair_identificador(f, "projetos_objetivos_"): f
    for f in arquivos_objetivos
}

mapa_pbl = {
    extrair_identificador(f, "projetos_pbl_"): f
    for f in arquivos_pbl
}

print("Objetivos encontrados:", list(mapa_objetivos.keys()))
print("PBL encontrados:", list(mapa_pbl.keys()))

identificadores_comuns = sorted(
    set(mapa_objetivos.keys()) &
    set(mapa_pbl.keys())
)

if not identificadores_comuns:
    print("❌ Nenhum par correspondente encontrado.")
    print("Verifique se os sufixos dos arquivos são idênticos.")
    exit()

# ==========================================================
# 🚀 Processamento por disciplina
# ==========================================================

for id_comum in identificadores_comuns:

    print(f"\n🚀 Processando disciplina: {id_comum}")

    objetivos = carregar_objetivos_json(mapa_objetivos[id_comum])
    projetos = carregar_projetos_json(mapa_pbl[id_comum])

    # Inicializar matriz LO × PBL
    matriz = {
        lo: {pbl: 0 for pbl in projetos}
        for lo in objetivos
    }

    # ======================================================
    # 🔁 Para cada LO → rankear PBLs
    # ======================================================

    for lo in objetivos:

        print(f"   🔎 Avaliando Objetivo: {lo[:60]}...")

        prompt = f"""
Dado o objetivo de aprendizagem abaixo e a lista de projetos PBL,
liste os {K} projetos que melhor desenvolvem este objetivo,
em ordem de relevância (do mais relevante para o menos relevante).

Objetivo de Aprendizagem:
{lo}

Projetos PBL:
{chr(10).join(projetos)}

Responda apenas com a lista numerada dos projetos escolhidos.
Não explique.
"""

        resposta = chamar_gemini(prompt)

        if not resposta:
            continue

        linhas_resposta = resposta.split("\n")

        posicao = 1

        for linha in linhas_resposta:
            linha = linha.strip()

            if not linha:
                continue

            for pbl in projetos:
                if pbl.lower() in linha.lower():
                    if matriz[lo][pbl] == 0:

                        # Score linear decrescente
                        score = K - (posicao - 1)
                        matriz[lo][pbl] = score

                        posicao += 1
                    break

            if posicao > K:
                break

        time.sleep(SLEEP_SECONDS)

    # ======================================================
    # 💾 Gerar CSV
    # ======================================================

    nome_csv = os.path.join(
        DATA_PROCESSED_DIR,
        f"PBL_LO_{id_comum}.csv"
    )

    with open(nome_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["Learning Objective"] + projetos)

        for lo in objetivos:
            linha = [lo] + [matriz[lo][pbl] for pbl in projetos]
            writer.writerow(linha)

    print(f"   ✅ Matriz salva em: {nome_csv}")

print("\n✅ Todas as matrizes foram geradas com sucesso!")
