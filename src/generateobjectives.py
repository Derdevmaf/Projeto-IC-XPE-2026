from google import genai
import os
from dotenv import load_dotenv
import re
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==============================
# 1️⃣ GERAR OBJETIVOS EM JSON
# ==============================

prompt_objetivos = """
Gere 15 objetivos de aprendizagem para a disciplina Aprendizado por Reforço.

IMPORTANTE:
- A saída deve ser SOMENTE um JSON válido.
- Não escreva explicações.
- Não use markdown.
- Não escreva ```json.
- Retorne apenas um array JSON com 15 objetos.

Cada objeto deve conter EXATAMENTE o seguinte campo:

{
  "objetivo_de_apendizagem": string
}

Regras:
- Objetivos devem aumentar progressivamente em complexidade.
- Linguagem clara, técnica e mensurável.
- Não invente campos extras.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_objetivos
)

resposta_texto = response.text.strip()

# ==============================
# 2️⃣ EXTRAIR NOME DA DISCIPLINA
# ==============================

match = re.search(r"disciplina (.+?)\.", prompt_objetivos)
disciplina = match.group(1) if match else "disciplina"

disciplina_formatada = (
    disciplina.lower()
    .replace(" ", "_")
    .replace("ç", "c")
    .replace("ã", "a")
    .replace("á", "a")
)

# Caminho absoluto baseado na estrutura do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_RAW = os.path.join(BASE_DIR, "data", "raw")

# Garante que a pasta exista
os.makedirs(PASTA_RAW, exist_ok=True)

nome_arquivo = os.path.join(
    PASTA_RAW,
    f"projetos_objetivos_{disciplina_formatada}.json"
)


# ==============================
# 3️⃣ VALIDAR JSON
# ==============================

try:
    dados_json = json.loads(resposta_texto)

    if not isinstance(dados_json, list):
        raise ValueError("A resposta não é uma lista JSON.")

    if len(dados_json) != 15:
        raise ValueError("A lista não contém exatamente 15 objetivos.")

    # Validar estrutura
    for obj in dados_json:
        if set(obj.keys()) != {"objetivo_de_apendizagem"}:
            raise ValueError("Um ou mais objetos possuem campos incorretos.")

    # Salvar JSON validado
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados_json, f, indent=2, ensure_ascii=False)

    print(f"✅ Objetivos gerados com sucesso! Arquivo: {nome_arquivo}")

except (json.JSONDecodeError, ValueError) as e:
    print("❌ Erro ao validar JSON gerado pela IA:")
    print(e)
    print("\nResposta recebida:")
    print(resposta_texto)
