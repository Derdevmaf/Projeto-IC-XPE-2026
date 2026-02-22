import os
import json
import csv
import networkx as nx
import matplotlib.pyplot as plt

# ==============================
# 📂 Caminhos
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

INPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "LO_to_PBLs.json"
)

OUTPUT_MATRIX = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "matriz_PBL_x_PBL.csv"
)

OUTPUT_IMAGE = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "grafo_PBL.png"
)

# ==============================
# 🧼 Função de normalização
# ==============================

def normalizar(texto):
    return texto.strip().lower()

# ==============================
# 📥 Carregar LO → PBLs
# ==============================

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    dados = json.load(f)

# ==============================
# 🔄 Construir PBL → LO (com limpeza)
# ==============================

pbl_to_lo = {}

for item in dados:
    lo = normalizar(item["LO"])

    for pbl in item["PBLs"]:
        pbl_norm = normalizar(pbl)

        if pbl_norm not in pbl_to_lo:
            pbl_to_lo[pbl_norm] = set()

        pbl_to_lo[pbl_norm].add(lo)

pbls = list(pbl_to_lo.keys())

# ==============================
# 🔎 DEBUG — Verificar duplicação
# ==============================

print("\n===== DEBUG =====")
print("Total de PBLs:", len(pbls))
print("Total únicos:", len(set(pbls)))
print("=================\n")

# ==============================
# 🧠 Criar matriz PBL x PBL
# ==============================

matriz = []

for pbl_a in pbls:
    linha = {"PBL": pbl_a}
    lo_a = pbl_to_lo[pbl_a]

    for pbl_b in pbls:
        if pbl_a == pbl_b:
            linha[pbl_b] = 0
        else:
            lo_b = pbl_to_lo[pbl_b]

            # Dependência se LO(A) ⊂ LO(B)
            if lo_a.issubset(lo_b) and lo_a != lo_b:
                linha[pbl_b] = 1
            else:
                linha[pbl_b] = 0

    matriz.append(linha)

# ==============================
# 💾 Salvar matriz CSV
# ==============================

colunas = ["PBL"] + pbls

with open(OUTPUT_MATRIX, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=colunas)
    writer.writeheader()
    writer.writerows(matriz)

print("✅ Matriz PBL x PBL salva com sucesso!")

# ==============================
# 🌐 Criar grafo direcionado
# ==============================

G = nx.DiGraph()

for pbl in pbls:
    G.add_node(pbl)

for linha in matriz:
    origem = linha["PBL"]
    for destino in pbls:
        if linha[destino] == 1:
            G.add_edge(origem, destino)

# ==============================
# 🔝 Ordenação Topológica
# ==============================

print("\n===== ORDENAÇÃO TOPOLÓGICA =====")

if nx.is_directed_acyclic_graph(G):
    ordem = list(nx.topological_sort(G))

    for i, pbl in enumerate(ordem, start=1):
        print(f"{i}. {pbl}")

    print(f"\nTotal na ordenação: {len(ordem)}")

else:
    print("❌ O grafo contém ciclos! Não é possível realizar ordenação topológica.")

# ==============================
# 🎨 Desenhar grafo
# ==============================

plt.figure(figsize=(14, 10))

pos = nx.spring_layout(G, seed=42)

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=2500,
    node_color="lightblue",
    font_size=8,
    arrows=True
)

plt.title("Grafo de Dependência entre PBLs")

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300)
plt.close()

print("✅ Grafo gerado com sucesso!")
print(f"Imagem salva em: {OUTPUT_IMAGE}")