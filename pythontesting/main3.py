import pandas as pd

# Carregar dados
df = pd.read_csv("../data/processed/LO_PBL_programacao_python.csv")

# Criar matriz binária
matriz_binaria = (df.iloc[:, 1:] > 0).astype(int)

# LO → número de PBLs
lo_counts = matriz_binaria.sum(axis=1)

# PBL → número de LOs
pbl_counts = matriz_binaria.sum(axis=0)

# Criar DataFrame combinado
df_combined = pd.DataFrame({
    "Learning Objectives": df["Learning Objective"],
    "#PBLs": lo_counts,
    "PBL": matriz_binaria.columns,
    "#Learning Objectives": pbl_counts.values
})

print(df_combined)

# Salvar
df_combined.to_csv("LO_PBL_side_by_side.csv", index=False)
