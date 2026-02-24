import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# =====================================
# 🔐 Configuração OpenAI
# =====================================

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY não encontrada no .env")

client = OpenAI(api_key=api_key)
MODEL = "gpt-4o-mini"

# =====================================
# 📂 Caminhos
# =====================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OBJETIVOS_PATH = os.path.join(
    BASE_DIR, "data", "raw", "projetos_objetivos_programacao_python.json"
)

PBL_PATH = os.path.join(
    BASE_DIR, "data", "raw", "projetos_pbl_programacao_python.json"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "mapeamento_pbl_objetivos_programacao_python.json"
)

CHECKPOINT_PATH = os.path.join(
    OUTPUT_DIR,
    "checkpoint_mapeamento.json"
)

# =====================================
# 📥 Carregar Dados
# =====================================

with open(OBJETIVOS_PATH, "r", encoding="utf-8") as f:
    objetivos = json.load(f)

with open(PBL_PATH, "r", encoding="utf-8") as f:
    pbls = json.load(f)

print(f"📚 Total de PBLs: {len(pbls)}")
print(f"🎯 Total de Objetivos: {len(objetivos)}")
print("🚀 Iniciando processamento...\n")

# =====================================
# 🔁 Retry automático
# =====================================

def call_with_retry(prompt, retries=3):
    for tentativa in range(retries):
        try:
            response = client.responses.create(
                model=MODEL,
                input=[
                    {
                        "role": "system",
                        "content": "Responda APENAS com JSON válido. Não use markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )
            return response
        except Exception as e:
            print(f"⚠️ Tentativa {tentativa+1} falhou: {e}")
            time.sleep(2)

    raise Exception("❌ Falha após múltiplas tentativas")

# =====================================
# 🧹 Limpeza segura de JSON
# =====================================

def limpar_json(texto):
    texto = texto.strip()

    if texto.startswith("```"):
        partes = texto.split("```")
        if len(partes) >= 2:
            texto = partes[1]

    return texto.strip()

# =====================================
# 🤖 Avaliação do PBL
# =====================================

def avaliar_pbl_completo(projeto, objetivos, indice):

    lista_objetivos = ""
    for i, obj in enumerate(objetivos):
        lista_objetivos += f"{i} - {obj['objetivo_de_aprendizagem']}\n"

    prompt = f"""
Analise o seguinte projeto PBL e os objetivos disponíveis.

Projeto:
Nome: {projeto["nome_do_projeto"]}
Aula: {projeto["nome_da_aula"]}
Descrição: {projeto["descricao_resumida"]}
Objetivo do projeto: {projeto["objetivo_de_aprendizagem"]}

Objetivos disponíveis:
{lista_objetivos}

TAREFAS:

1) Para cada objetivo, informe se é necessário dominá-lo para executar o projeto.
   Use apenas "sim" ou "nao".

2) Avalie a dificuldade do projeto considerando:
   - complexidade_cognitiva (1-5)
   - dependencia_previa (1-5)
   - abstracao (1-5)
   - nivel (1-5)
   - justificativa curta

Responda obrigatoriamente neste formato:

{{
  "objetivos": {{
    "0": "sim",
    "1": "nao"
  }},
  "dificuldade": {{
    "nivel": 3,
    "complexidade_cognitiva": 3,
    "dependencia_previa": 4,
    "abstracao": 2,
    "justificativa": "texto curto"
  }}
}}
"""

    print(f"📌 Processando PBL {indice}/{len(pbls)}: {projeto['nome_do_projeto']}")

    response = call_with_retry(prompt)

    texto = limpar_json(response.output_text)

    try:
        return json.loads(texto)
    except Exception as e:
        print("❌ Erro ao converter JSON. Resposta recebida:")
        print(texto)
        raise e

# =====================================
# 🔄 Processamento Principal
# =====================================

resultado_final = []

# Carregar checkpoint se existir
if os.path.exists(CHECKPOINT_PATH):
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        resultado_final = json.load(f)
    print(f"🔄 Checkpoint carregado ({len(resultado_final)} PBLs já processados)")

inicio_total = time.time()

for i, pbl in enumerate(pbls, 1):

    # Pular se já processado
    if any(r["nome_do_projeto"] == pbl["nome_do_projeto"] for r in resultado_final):
        continue

    resultado_modelo = avaliar_pbl_completo(pbl, objetivos, i)

    # ==========================
    # Processar objetivos
    # ==========================

    relacoes = []

    for indice_obj, resposta in resultado_modelo["objetivos"].items():
        objetivo_texto = objetivos[int(indice_obj)]["objetivo_de_aprendizagem"]

        relacoes.append({
            "objetivo": objetivo_texto,
            "demanda": resposta
        })

    # ==========================
    # Processar dificuldade
    # ==========================

    dif = resultado_modelo["dificuldade"]

    score_normalizado = (
        dif["complexidade_cognitiva"] +
        dif["dependencia_previa"] +
        dif["abstracao"]
    ) / 15  # Normalização 0–1

    resultado_final.append({
        "nome_do_projeto": pbl["nome_do_projeto"],
        "mapeamento_objetivos": relacoes,
        "dificuldade": {
            "nivel": dif["nivel"],
            "score_normalizado": round(score_normalizado, 3),
            "criterios": {
                "complexidade_cognitiva": dif["complexidade_cognitiva"],
                "dependencia_previa": dif["dependencia_previa"],
                "abstracao": dif["abstracao"]
            },
            "justificativa": dif["justificativa"]
        }
    })

    # Salvar checkpoint após cada PBL
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)

fim_total = time.time()

print(f"\n⏱ Tempo total: {(fim_total - inicio_total)/60:.2f} minutos")

# =====================================
# 💾 Salvar Resultado Final
# =====================================

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, indent=2, ensure_ascii=False)

print(f"💾 Arquivo salvo em: {OUTPUT_PATH}")
print("🎉 Mapeamento concluído com sucesso!")