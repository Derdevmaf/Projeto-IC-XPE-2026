import pandas as pd

# 1️⃣ Carregar a matriz (LO nas linhas, PBLs nas colunas)
df = pd.read_csv("../data/processed/LO_PBL_programacao_python.csv")

# 2️⃣ Transformar em presença binária (1 se >0, 0 se 0)
matriz_binaria = (df.iloc[:, 1:] > 0).astype(int)

# 3️⃣ Contar quantos PBLs utilizam cada LO
lo_counts = matriz_binaria.sum(axis=1)

# 4️⃣ Criar tabela final
df_lo_pbls = pd.DataFrame({
    "Learning Objective": df["Learning Objective"],
    "#PBLs": lo_counts
})

# 5️⃣ Ordenar do maior para o menor
df_lo_pbls = df_lo_pbls.sort_values("#PBLs", ascending=True)

# 6️⃣ Mostrar tabela
print(df_lo_pbls)

df_lo_pbls.to_csv("LO_vs_PBLs.csv", index=False)
