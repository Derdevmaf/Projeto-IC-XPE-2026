import os
import json
import time
from dotenv import load_dotenv
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
# 📂 Caminhos dos arquivos
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OBJETIVOS_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "projetos_objetivos_programacao_python.json"
)

PBL_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "projetos_pbl_programacao_python.json"
)

OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "mapeamento_pbl_objetivos_programacao_python.json"
)

# ==============================
# 📥 Carregar dados
# ==============================

with open(OBJETIVOS_PATH, "r", encoding="utf-8") as f:
    objetivos = json.load(f)

with open(PBL_PATH, "r", encoding="utf-8") as f:
    pbls = json.load(f)

total_cruzamentos = len(pbls) * len(objetivos)

print(f"📚 Total de PBLs: {len(pbls)}")
print(f"🎯 Total de Objetivos: {len(objetivos)}")
print(f"🔄 Total de cruzamentos: {total_cruzamentos}")
print("🚀 Iniciando processamento...\n")

# ==============================
# 🤖 Função para avaliar relação
# ==============================

def avaliar_relacao(projeto, objetivo, contador_atual):
    prompt = f"""
    Analise o seguinte projeto PBL e o objetivo de aprendizagem.

    Projeto:
    Nome: {projeto["nome_do_projeto"]}
    Aula: {projeto["nome_da_aula"]}
    Descrição: {projeto["descricao_resumida"]}
    Objetivo do projeto: {projeto["objetivo_de_aprendizagem"]}

    Objetivo de aprendizagem:
    {objetivo["objetivo_de_aprendizagem"]}

    Pergunta:
    Para executar corretamente este projeto, o aluno precisa dominar esse objetivo?

    Responda SOMENTE com:
    sim
    ou
    nao
    """

    print(f"🔎 [{contador_atual}/{total_cruzamentos}] Enviando para OpenAI...")
    inicio = time.time()

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    fim = time.time()
    print(f"✅ Resposta recebida ({fim - inicio:.2f}s)")

    resposta = response.output_text.strip().lower()

    if "sim" in resposta:
        return "sim"
    return "nao"

# ==============================
# 🔄 Processar todos os cruzamentos
# ==============================

resultado_final = []
contador = 0
inicio_total = time.time()

for i, pbl in enumerate(pbls, 1):
    print(f"\n📌 Processando PBL {i}/{len(pbls)}: {pbl['nome_do_projeto']}")
    relacoes = []

    for objetivo in objetivos:
        contador += 1
        resposta = avaliar_relacao(pbl, objetivo, contador)

        relacoes.append({
            "objetivo": objetivo["objetivo_de_aprendizagem"],
            "demanda": resposta
        })

    resultado_final.append({
        "nome_do_projeto": pbl["nome_do_projeto"],
        "mapeamento_objetivos": relacoes
    })

fim_total = time.time()

print(f"\n⏱ Tempo total de execução: {(fim_total - inicio_total)/60:.2f} minutos")

# ==============================
# 💾 Salvar resultado
# ==============================

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, indent=2, ensure_ascii=False)

print(f"💾 Arquivo salvo em: {OUTPUT_PATH}")
print("🎉 Mapeamento concluído com sucesso!")