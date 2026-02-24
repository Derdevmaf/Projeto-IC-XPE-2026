import os
from dotenv import load_dotenv
import re
import json
from openai import OpenAI

load_dotenv()

# ==============================
# 🔐 Configurar OpenAI
# ==============================

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY não encontrada no .env")

client = OpenAI(api_key=openai_api_key)

MODEL = "gpt-4o-mini"

# ==============================
# 1️⃣ GERAR OBJETIVOS EM JSON
# ==============================

prompt_objetivos = """
Gere 50 objetivos de aprendizagem para a disciplina Aprendizado por Reforço.

IMPORTANTE:
- A saída deve ser SOMENTE um JSON válido.
- Não escreva explicações.
- Não use markdown.
- Não escreva ```json.
- Retorne apenas um array JSON com 50 objetos.

Cada objeto deve conter EXATAMENTE o seguinte campo:

{
  "objetivo_de_aprendizagem": string
}

Regras:
- Objetivos devem aumentar progressivamente em complexidade.
- Linguagem clara, técnica e mensurável.
- Não invente campos extras.
"""

try:
    response = client.responses.create(
        model=MODEL,
        input=prompt_objetivos
    )

    resposta_texto = response.output_text.strip()

except Exception as e:
    print("❌ Erro ao chamar OpenAI:")
    print(e)
    exit()


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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_RAW = os.path.join(BASE_DIR, "data", "raw")

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

    for obj in dados_json:
        if set(obj.keys()) != {"objetivo_de_aprendizagem"}:
            raise ValueError("Um ou mais objetos possuem campos incorretos.")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados_json, f, indent=2, ensure_ascii=False)

    print(f"✅ Objetivos gerados com sucesso! Arquivo: {nome_arquivo}")

except (json.JSONDecodeError, ValueError) as e:
    print("❌ Erro ao validar JSON gerado pela IA:")
    print(e)
    print("\nResposta recebida:")
    print(resposta_texto)
