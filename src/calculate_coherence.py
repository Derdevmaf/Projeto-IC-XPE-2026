import os
import json
import csv
import networkx as nx

# ==============================
# 📂 Caminhos
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

MATRIZ_LO_PBL_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "matriz_LO_x_PBL.csv"
)

MATRIZ_PBL_PBL_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "matriz_PBL_x_PBL.csv"
)

# ==============================
# ⚙️ Parâmetros configuráveis
# ==============================

IDEAL_PBL_PER_LO = 1.0

PESO_COBERTURA = 0.3
PESO_EQUILIBRIO = 0.3
PESO_PROGRESSAO = 0.4


def calcular_coerencia():

    print("="*50)
    print("📊 CÁLCULO DO SCORE DE COERÊNCIA DE ENSINO")
    print("="*50)

    # ==============================
    # 1️⃣ Ler matriz LO x PBL
    # ==============================

    if not os.path.exists(MATRIZ_LO_PBL_PATH):
        print("❌ Erro: matriz_LO_x_PBL.csv não encontrada.")
        return

    los = []
    pbl_cobertura = {}

    with open(MATRIZ_LO_PBL_PATH, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        # nomes das colunas PBL
        pbls_names = [col for col in reader.fieldnames if col != "LO"]

        for pbl in pbls_names:
            pbl_cobertura[pbl] = []

        for row in reader:

            lo_name = row["LO"]
            los.append(lo_name)

            for pbl in pbls_names:

                if int(row.get(pbl, 0)) == 1:
                    pbl_cobertura[pbl].append(lo_name)

    total_los = len(los)
    total_pbls = len(pbls_names)

    # ==============================
    # 2️⃣ Cobertura de LOs
    # ==============================

    los_cobertos = set()

    for pbl, lo_list in pbl_cobertura.items():
        for lo in lo_list:
            los_cobertos.add(lo)

    s_coverage = len(los_cobertos) / total_los if total_los > 0 else 0

    print(f"🔸 Cobertura de LOs: {len(los_cobertos)} / {total_los} (Score: {s_coverage:.2f})")

    # ==============================
    # 3️⃣ Equilíbrio LO ↔ PBL
    # ==============================

    pbls_ideais = total_los * IDEAL_PBL_PER_LO

    desvio = abs(total_pbls - pbls_ideais)

    s_balance = max(0.0, 1.0 - (desvio / pbls_ideais)) if pbls_ideais > 0 else 0

    if total_pbls > pbls_ideais:

        print(f"🔸 Equilíbrio (Redundância/Excesso): {total_pbls} PBLs para {total_los} LOs.")
        print("   -> Excesso de projetos causa mapeamento ineficiente.")

    elif total_pbls < pbls_ideais:

        print(f"🔸 Equilíbrio (Sobrecarga): {total_pbls} PBLs para {total_los} LOs.")
        print("   -> Poucos projetos limitam a absorção dos conteúdos.")

    else:

        print(f"🔸 Equilíbrio Perfeito: {total_pbls} PBLs para {total_los} LOs.")

    print(f"   -> Score de Equilíbrio: {s_balance:.2f}")

    # ==============================
    # 4️⃣ Ler matriz PBL x PBL
    # ==============================

    if not os.path.exists(MATRIZ_PBL_PBL_PATH):

        print("❌ Erro: matriz_PBL_x_PBL.csv não encontrada.")
        return

    G = nx.DiGraph()

    for pbl in pbls_names:
        G.add_node(pbl)

    with open(MATRIZ_PBL_PBL_PATH, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        # nomes das colunas da matriz PBL-PBL
        pbl_columns = [col for col in reader.fieldnames if col != "PBL"]

        for row in reader:

            pbl_origem = row["PBL"]

            for pbl_destino in pbl_columns:

                if int(row.get(pbl_destino, 0)) == 1:
                    G.add_edge(pbl_origem, pbl_destino)

    # ==============================
    # 5️⃣ Score de Progressão
    # ==============================

    if nx.is_directed_acyclic_graph(G):

        caminho_maximo = nx.dag_longest_path_length(G) + 1

        s_progression = caminho_maximo / total_pbls if total_pbls > 0 else 0

        print(f"🔸 Progressão Linear: Maior sequência possui {caminho_maximo} PBL(s).")
        print(f"   -> Score de Progressão: {s_progression:.2f}")

    else:

        print("🔸 Progressão Linear: O grafo possui ciclos (inconsistência nas dependências).")

        s_progression = 0

        print(f"   -> Score de Progressão: {s_progression:.2f}")

    # ==============================
    # 6️⃣ Score final
    # ==============================

    score_final = (
        s_coverage * PESO_COBERTURA +
        s_balance * PESO_EQUILIBRIO +
        s_progression * PESO_PROGRESSAO
    )

    print("="*50)
    print(f"🏆 SCORE DE COERÊNCIA FINAL: {score_final:.2f} / 1.00")
    print("="*50)

    # ==============================
    # 7️⃣ Análise textual
    # ==============================

    print("\n📝 ANÁLISE DO RESULTADO:")

    if score_final > 0.8:

        print("A estrutura está MUITO coerente.")

    elif score_final > 0.5:

        print("A estrutura possui coerência MODERADA.")

    else:

        print("A estrutura possui BAIXA coerência (desorganização pedagógica).")

    # Sugestões automáticas

    if desvio > 0:

        if total_pbls > pbls_ideais:

            print("\n💡 Sugestão 1: Reduza a quantidade de projetos ou combine projetos semelhantes.")

        else:

            print("\n💡 Sugestão 1: Aumente a quantidade de projetos para evitar sobrecarga de conteúdos.")

    if s_progression < 0.5:

        print("💡 Sugestão 2: Melhore a progressão entre projetos criando mais dependências pedagógicas.")


if __name__ == "__main__":

    calcular_coerencia()