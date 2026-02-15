import os
import glob
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# Carregar .env
load_dotenv()

# Criar cliente Gemini
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1"}
)

# Configuração
K = 15  # Número de itens a serem listados/ranqueados

def carregar_arquivo(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

def extrair_identificador(caminho_completo, prefixo):
    """
    Extrai o identificador a partir do nome do arquivo,
    ignorando caminho completo.
    """
    nome_base = os.path.basename(caminho_completo)
    return nome_base.replace(prefixo, "").replace(".txt", "")

def formatar_nome_exibicao(identificador):
    return identificador.replace("_", " ").strip().title()

def chamar_gemini_com_retry(prompt, max_retries=5):
    for i in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                import re
                match = re.search(r"retry in ([\d\.]+)s", error_msg)
                wait_time = float(match.group(1)) + 2 if match else 60
                
                print(f"   ⚠️ Limite de cota atingido. Aguardando {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ Erro na API: {e}")
                return None
    print("   ❌ Falha após múltiplas tentativas.")
    return None


# ===============================
# 📁 CONFIGURAÇÃO DE DIRETÓRIOS
# ===============================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# Criar pasta processed se não existir
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)


# Buscar arquivos em raw
arquivos_objetivos = glob.glob(os.path.join(DATA_RAW_DIR, "objetivos_aprendizagem_*.txt"))
arquivos_pbl = glob.glob(os.path.join(DATA_RAW_DIR, "projetos_pbl_*.txt"))

# Mapear identificadores corretamente
mapa_objetivos = {
    extrair_identificador(f, "objetivos_aprendizagem_"): f
    for f in arquivos_objetivos if "ranking" not in f
}

mapa_pbl = {
    extrair_identificador(f, "projetos_pbl_"): f
    for f in arquivos_pbl if "ranking" not in f
}

identificadores_comuns = sorted(list(set(mapa_objetivos.keys()) & set(mapa_pbl.keys())))

if not identificadores_comuns:
    print("❌ Nenhum par correspondente encontrado.")
    exit()

print(f"🔍 Encontrados {len(identificadores_comuns)} pares de arquivos.\n")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for id_comum in identificadores_comuns:
    caminho_obj = mapa_objetivos[id_comum]
    caminho_pbl = mapa_pbl[id_comum]
    disciplina_exibicao = formatar_nome_exibicao(id_comum)
    
    print(f"🚀 Processando: {disciplina_exibicao}")
    
    objetivos_texto = carregar_arquivo(caminho_obj)
    pbl_texto = carregar_arquivo(caminho_pbl)
    
    if not objetivos_texto or not pbl_texto:
        print(f"   ⚠️ Conteúdo vazio em {id_comum}")
        continue

    # ===============================
    # 1️⃣ RANKING DE OBJETIVOS
    # ===============================
    prompt_obj = f"""
    Analise os objetivos para {disciplina_exibicao}:
    {objetivos_texto}
    Ranqueie os {K} mais alinhados.
    """

    print("   --- Gerando Ranking de Objetivos ---")
    resultado_obj = chamar_gemini_com_retry(prompt_obj)
    
    if resultado_obj:
        nome_ranking_obj = os.path.join(
            DATA_PROCESSED_DIR,
            f"ranking_objetivos_{id_comum}_{timestamp}.txt"
        )
        with open(nome_ranking_obj, "w", encoding="utf-8") as f:
            f.write(resultado_obj)
        print(f"   ✅ Salvo: {nome_ranking_obj}")

    time.sleep(5)

    # ===============================
    # 2️⃣ RANKING DE PROJETOS
    # ===============================
    prompt_pbl = f"""
    Analise os projetos PBL para {disciplina_exibicao}:
    {pbl_texto}
    Ranqueie {K} por complexidade progressiva.
    """

    print("   --- Gerando Ranking de Projetos ---")
    resultado_pbl = chamar_gemini_com_retry(prompt_pbl)
    
    if resultado_pbl:
        nome_ranking_pbl = os.path.join(
            DATA_PROCESSED_DIR,
            f"ranking_projetos_{id_comum}_{timestamp}.txt"
        )
        with open(nome_ranking_pbl, "w", encoding="utf-8") as f:
            f.write(resultado_pbl)
        print(f"   ✅ Salvo: {nome_ranking_pbl}\n")

    time.sleep(10)

print("✅ Processamento concluído com sucesso!")
