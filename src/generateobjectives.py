import os
import re
from dotenv import load_dotenv
from google import genai

# Carregar .env
load_dotenv()

# Criar cliente (API estável)
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1"}
)

# ==============================
# 1️⃣ GERAR OBJETIVOS
# ==============================

prompt_objetivos = """
Gere 15 objetivos de aprendizagem para a disciplina Aprendendo Javascript.

Regras:
- Liste exatamente 15 objetivos.
- Um por linha.
- Numerados de 1 a 15.
- Seja específico e progressivo em complexidade.
"""

response_obj = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_objetivos
)

objetivos_texto = response_obj.text

# 🔎 Extrair nome da disciplina
match = re.search(r"disciplina (.+?)\.", prompt_objetivos)
disciplina = match.group(1) if match else "disciplina"

# 🧹 Normalizar nome para arquivo
disciplina_formatada = (
    disciplina.lower()
    .replace(" ", "_")
    .replace("ç", "c")
    .replace("ã", "a")
    .replace("á", "a")
)

nome_arquivo = f"objetivos_aprendizagem_{disciplina_formatada}.txt"

with open(nome_arquivo, "w", encoding="utf-8") as f:
    f.write(objetivos_texto)

print(f"✅ Objetivos gerados! Arquivo: {nome_arquivo}")
