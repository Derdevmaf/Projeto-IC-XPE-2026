import pandas as pd

# 1️⃣ Carregar a matriz (LO nas linhas, PBLs nas colunas)
df = pd.read_csv("../data/processed/LO_PBL_aprendizado_por_reforco.csv")

# 2️⃣ Criar matriz binária (1 se >0, 0 se 0)
matriz_binaria = (df.iloc[:, 1:] > 0).astype(int)

# 3️⃣ Contar quantos LOs cada PBL cobre
pbl_counts = matriz_binaria.sum(axis=0)

# 4️⃣ Criar tabela final
df_pbl_los = pd.DataFrame({
    "PBL": matriz_binaria.columns,
    "#LOs": pbl_counts.values
})

# 5️⃣ Ordenar do maior para o menor
df_pbl_los = df_pbl_los.sort_values("#LOs", ascending=True)

# 6️⃣ Mostrar resultado
print(df_pbl_los)

df_pbl_los.to_csv("PBLs_vs_LO.csv", index=False)
