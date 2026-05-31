import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os

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
# 📂 Definir caminhos (FORMA SEGURA)
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_RAW = BASE_DIR / "data" / "raw"

arquivo_los = PASTA_RAW / "projetos_objetivos_programacao_python.json"

print("📂 BASE_DIR:", BASE_DIR)
print("📂 PASTA_RAW:", PASTA_RAW)
print("📂 Arquivo LOs:", arquivo_los)

if not arquivo_los.exists():
    raise FileNotFoundError(
        f"❌ Arquivo de LOs não encontrado em: {arquivo_los}"
    )

# ==============================
# 0️⃣ Carregar LOs
# ==============================

with open(arquivo_los, "r", encoding="utf-8") as f:
    lista_los = json.load(f)

if not isinstance(lista_los, list):
    raise ValueError("❌ O arquivo de LOs não contém uma lista válida.")

total_los = len(lista_los)
total_projetos_esperado = total_los * 2

print(f"📚 Total de LOs encontrados: {total_los}")
print(f"🧠 Total esperado de PBLs: {total_projetos_esperado}")

# ==============================
# 1️⃣ Gerar PBLs baseados nos LOs
# ==============================

prompt_pbl = f"""
Você receberá uma lista de Objetivos de Aprendizagem (LOs) em formato JSON.

Sua tarefa:
- Gerar EXATAMENTE 2 projetos PBL para CADA LO.
- Total esperado: {total_projetos_esperado} projetos.
- Cada projeto deve exercitar diretamente o LO correspondente.
- Para cada LO, os dois projetos devem ter complexidade crescente.

IMPORTANTE:
- A saída deve ser SOMENTE um JSON válido.
- Não escreva explicações.
- Não use markdown.
- Não escreva ```json.
- Retorne apenas um array JSON com {total_projetos_esperado} objetos.

Cada objeto deve conter EXATAMENTE os seguintes campos:

{{
  "nome_do_projeto": string,
  "nome_da_aula": string,
  "descricao_resumida": string,
  "objetivo_de_aprendizagem": string,
  "unidades_de_conhecimento_utilizadas": array de strings,
  "tags": array de strings,
  "nivel_complexidade": "iniciante" | "intermediario" | "avancado"
}}

Regras:
- O campo "objetivo_de_aprendizagem" deve ser idêntico ao LO fornecido.
- Não invente novos LOs.
- Não invente campos extras.
- Linguagem técnica e clara.
- Complexidade deve evoluir ao longo da lista.

Lista de LOs:
{json.dumps(lista_los, ensure_ascii=False)}
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
# 2️⃣ Validar JSON
# ==============================

try:
    dados_json = json.loads(resposta_texto)

    if not isinstance(dados_json, list):
        raise ValueError("A resposta não é uma lista JSON.")

    if len(dados_json) != total_projetos_esperado:
        raise ValueError(
            f"A lista não contém exatamente {total_projetos_esperado} projetos."
        )

    campos_obrigatorios = {
        "nome_do_projeto",
        "nome_da_aula",
        "descricao_resumida",
        "objetivo_de_aprendizagem",
        "unidades_de_conhecimento_utilizadas",
        "tags",
        "nivel_complexidade"
    }

    los_validos = [
        lo["objetivo_de_aprendizagem"] for lo in lista_los
    ]

    # Contador para garantir exatamente 2 projetos por LO
    contador_por_lo = {lo: 0 for lo in los_validos}

    for projeto in dados_json:
        if set(projeto.keys()) != campos_obrigatorios:
            raise ValueError("Um ou mais objetos possuem campos incorretos.")

        lo_projeto = projeto["objetivo_de_aprendizagem"]

        if lo_projeto not in los_validos:
            raise ValueError(
                f"Projeto contém LO inexistente: {lo_projeto}"
            )

        contador_por_lo[lo_projeto] += 1

    # Verificar se cada LO tem exatamente 2 projetos
    for lo, quantidade in contador_por_lo.items():
        if quantidade != 2:
            raise ValueError(
                f"O LO '{lo}' não possui exatamente 2 projetos."
            )

    # ==============================
    # 3️⃣ Salvar arquivo
    # ==============================

    nome_arquivo_saida = PASTA_RAW / "projetos_pbl_por_lo.json"

    with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(dados_json, f, indent=2, ensure_ascii=False)

    print("✅ PBLs gerados com sucesso!")
    print(f"📁 Arquivo salvo em: {nome_arquivo_saida}")

except (json.JSONDecodeError, ValueError) as e:
    print("❌ Erro ao validar JSON gerado pela IA:")
    print(e)
    print("\nResposta recebida:")
    print(resposta_texto)