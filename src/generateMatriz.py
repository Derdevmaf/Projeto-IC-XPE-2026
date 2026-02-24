import os
import json
import csv

# ==============================
# 📂 Caminhos
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

INPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "mapeamento_pbl_objetivos_aprendizado_por_reforco.json"
)

OUTPUT_CSV = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "matriz_LO_x_PBL.csv"
)

OUTPUT_JSON = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "LO_to_PBLs.json"
)

# ==============================
# 📥 Carregar dados
# ==============================

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    dados = json.load(f)

# ==============================
# 🧠 Extrair nomes
# ==============================

pbls = [projeto["nome_do_projeto"] for projeto in dados]
los = [item["objetivo"] for item in dados[0]["mapeamento_objetivos"]]

# ==============================
# 🔄 1️⃣ Construir MATRIZ BINÁRIA (para CSV)
# ==============================

matriz_binaria = []

for i, lo in enumerate(los):
    linha = {"LO": lo}

    for projeto in dados:
        nome_pbl = projeto["nome_do_projeto"]
        demanda = projeto["mapeamento_objetivos"][i]["demanda"]
        linha[nome_pbl] = 1 if demanda == "sim" else 0

    matriz_binaria.append(linha)

# Salvar CSV
colunas = ["LO"] + pbls

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=colunas)
    writer.writeheader()
    writer.writerows(matriz_binaria)

# ==============================
# 🔄 2️⃣ Construir JSON agregado (LO → lista de PBLs)
# ==============================

estrutura_json = []

for linha in matriz_binaria:
    lo = linha["LO"]
    pbls_relacionados = [
        pbl for pbl in pbls
        if linha[pbl] == 1
    ]

    estrutura_json.append({
        "LO": lo,
        "PBLs": pbls_relacionados
    })

# Salvar JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(estrutura_json, f, indent=2, ensure_ascii=False)

# ==============================
# ✅ Final
# ==============================

print("✅ CSV (matriz binária) gerado com sucesso!")
print(f"→ {OUTPUT_CSV}")

print("✅ JSON (LO → lista de PBLs) gerado com sucesso!")
print(f"→ {OUTPUT_JSON}")