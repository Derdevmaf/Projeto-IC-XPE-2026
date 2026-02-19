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
# 1️⃣ GERAR PBL EM JSON
# ==============================

prompt_pbl = """
Gere 15 projetos PBL (Project-Based Learning) para a disciplina Programação Python.

IMPORTANTE:
- A saída deve ser SOMENTE um JSON válido.
- Não escreva explicações.
- Não use markdown.
- Não escreva ```json.
- Retorne apenas um array JSON com 15 objetos.

Cada objeto deve conter EXATAMENTE os seguintes campos:

{
  "nome_do_projeto": string,
  "nome_da_aula": string,
  "descricao_resumida": string,
  "objetivo_de_aprendizagem": string,
  "unidades_de_conhecimento_utilizadas": array de strings,
  "tags": array de strings,
  "nivel_complexidade": "iniciante" | "intermediario" | "avancado"
}

Regras:
- Projetos devem aumentar progressivamente em complexidade.
- Linguagem clara e técnica.
- Não invente campos extras.
"""

try:
    response = client.responses.create(
        model=MODEL,
        input=prompt_pbl
    )

    resposta_texto = response.output_text.strip()

except Exception as e:
    print("❌ Erro ao chamar OpenAI:")
    print(e)
    exit()


# ==============================
# 2️⃣ EXTRAIR NOME DA DISCIPLINA
# ==============================

match = re.search(r"disciplina (.+?)\.", prompt_pbl)
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
    f"projetos_pbl_{disciplina_formatada}.json"
)

# ==============================
# 3️⃣ VALIDAR JSON
# ==============================

try:
    dados_json = json.loads(resposta_texto)

    if not isinstance(dados_json, list):
        raise ValueError("A resposta não é uma lista JSON.")

    if len(dados_json) != 15:
        raise ValueError("A lista não contém exatamente 15 projetos.")

    campos_obrigatorios = {
        "nome_do_projeto",
        "nome_da_aula",
        "descricao_resumida",
        "objetivo_de_aprendizagem",
        "unidades_de_conhecimento_utilizadas",
        "tags",
        "nivel_complexidade"
    }

    for projeto in dados_json:
        if set(projeto.keys()) != campos_obrigatorios:
            raise ValueError("Um ou mais objetos possuem campos incorretos.")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados_json, f, indent=2, ensure_ascii=False)

    print(f"✅ PBLs gerados com sucesso! Arquivo: {nome_arquivo}")

except (json.JSONDecodeError, ValueError) as e:
    print("❌ Erro ao validar JSON gerado pela IA:")
    print(e)
    print("\nResposta recebida:")
    print(resposta_texto)
