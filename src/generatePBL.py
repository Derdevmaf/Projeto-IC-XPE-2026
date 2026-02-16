from google import genai
import os
from dotenv import load_dotenv
import re

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt_pbl = """
Gere 15 projetos PBL (Project-Based Learning) para a disciplina Aprendendo Javascript.

Regras:
- Liste exatamente 15 projetos.
- Um por linha.
- Numerados de 1 a 15.
- Projetos devem aumentar progressivamente em complexidade.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_pbl
)

pbl_texto = response.text

# 🔎 Extrair nome da disciplina do prompt
match = re.search(r"disciplina (.+?)\.", prompt_pbl)
disciplina = match.group(1) if match else "disciplina"

# 🧹 Normalizar nome para arquivo
disciplina_formatada = (
    disciplina.lower()
    .replace(" ", "_")
    .replace("ç", "c")
    .replace("ã", "a")
    .replace("á", "a")
)

nome_arquivo = f"projetos_pbl_{disciplina_formatada}.txt"

with open(nome_arquivo, "w", encoding="utf-8") as f:
    f.write(pbl_texto)

print(f"✅ PBLs gerados com sucesso! Arquivo: {nome_arquivo}")
