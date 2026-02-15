import os
import glob
import time
import re
import csv
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# ==========================================================
# 🔐 Carregar .env
# ==========================================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1"}
)

# ==========================================================
# ⚙ Configuração
# ==========================================================

K = 5  # Top K objetivos por projeto

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

def carregar_linhas(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    objetivos = []
    for linha in linhas:
        linha = linha.strip()
        if re.match(r"^\d+\.", linha):
            objetivos.append(linha)

    return objetivos

def extrair_identificador(caminho_completo, prefixo):
    nome_base = os.path.basename(caminho_completo)
    return nome_base.replace(prefixo, "").replace(".txt", "")

def chamar_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ==========================================================
# 🔎 Buscar arquivos
# ==========================================================

arquivos_objetivos = glob.glob(os.path.join(DATA_RAW_DIR, "objetivos_aprendizagem_*.txt"))
arquivos_pbl = glob.glob(os.path.join(DATA_RAW_DIR, "projetos_pbl_*.txt"))

mapa_objetivos = {
    extrair_identificador(f, "objetivos_aprendizagem_"): f
    for f in arquivos_objetivos
}

mapa_pbl = {
    extrair_identificador(f, "projetos_pbl_"): f
    for f in arquivos_pbl
}

identificadores_comuns = sorted(set(mapa_objetivos.keys()) & set(mapa_pbl.keys()))

if not identificadores_comuns:
    print("❌ Nenhum par correspondente encontrado.")
    exit()

# ==========================================================
# 🚀 Processamento por disciplina
# ==========================================================

for id_comum in identificadores_comuns:

    print(f"\n🚀 Processando disciplina: {id_comum}")

    objetivos = carregar_linhas(mapa_objetivos[id_comum])
    projetos = carregar_linhas(mapa_pbl[id_comum])

    # Inicializar matriz LO × PBL
    matriz = {lo: {pbl: 0 for pbl in projetos} for lo in objetivos}

    # ======================================================
    # Para cada PBL → rankear LOs
    # ======================================================

    for pbl in projetos:

        print(f"   🔎 Avaliando PBL: {pbl[:50]}...")

        prompt = f"""
        Dado o projeto abaixo e a lista de objetivos de aprendizagem,
        liste os {K} objetivos que este projeto mais exercita,
        em ordem de relevância.

        Projeto:
        {pbl}

        Objetivos:
        {chr(10).join(objetivos)}

        Responda apenas com a lista numerada dos objetivos escolhidos.
        """

        resposta = chamar_gemini(prompt)

        if not resposta:
            continue

        # Extrair ranking retornado
        linhas_resposta = resposta.split("\n")

        posicao = 1
        for linha in linhas_resposta:
            linha = linha.strip()

            if not linha:
                continue

            # Tenta encontrar qual LO foi citado
            for lo in objetivos:
                if lo.lower() in linha.lower():
                    matriz[lo][pbl] = posicao
                    posicao += 1
                    break

            if posicao > K:
                break

        time.sleep(3)

    # ======================================================
    # 💾 Gerar CSV
    # ======================================================

    nome_csv = os.path.join(
        DATA_PROCESSED_DIR,
        f"LO_PBL_{id_comum}.csv"
    )

    with open(nome_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Cabeçalho
        writer.writerow(["Learning Objective"] + projetos)

        # Linhas
        for lo in objetivos:
            linha = [lo] + [matriz[lo][pbl] for pbl in projetos]
            writer.writerow(linha)

    print(f"   ✅ Matriz salva em: {nome_csv}")

print("\n✅ Todas as matrizes foram geradas com sucesso!")
