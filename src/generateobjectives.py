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
Você é um especialista em design instrucional e em Inteligência Artificial. Gere 15 objetivos de aprendizagem para a disciplina "Aprendizado por Reforço" utilizando verbos da Taxonomia de Bloom.

Considere explicitamente os seguintes contextos pedagógicos ao estruturar os resultados:

* Nível do curso: graduação ou pós-graduação em Computação / Inteligência Artificial.
* Área do curso: Ciência da Computação, Ciência de Dados ou Inteligência Artificial.
* Pré-requisitos esperados: probabilidade, álgebra linear, cálculo básico, programação em Python e fundamentos de aprendizado de máquina.
* Natureza da disciplina: teórica e prática.
* Ferramentas comuns: Python, PyTorch ou TensorFlow, ambientes tipo Gym ou Gymnasium.

Tópicos esperados da disciplina:

* fundamentos de Aprendizado por Reforço
* Processos de Decisão de Markov (MDP)
* funções de valor
* equações de Bellman
* métodos Monte Carlo
* métodos de Diferença Temporal
* SARSA
* Q-Learning
* exploração vs exploração
* aproximação de função
* Deep Reinforcement Learning
* Policy Gradient
* métodos Actor-Critic

Aplicações possíveis:

* controle
* jogos
* robótica
* sistemas autônomos
* tomada de decisão sequencial

Os objetivos devem refletir progressão cognitiva conforme a Taxonomia de Bloom:
lembrar → compreender → aplicar → analisar → avaliar → criar.

IMPORTANTE:

* A saída deve ser SOMENTE um JSON válido.
* Não escreva explicações.
* Não use markdown.
* Não escreva ```json.

Estrutura da resposta:

* Retorne apenas um array JSON com 15 objetos.

Cada objeto deve conter EXATAMENTE o seguinte campo:

{
"objetivo_de_aprendizagem": string
}

Regras:

* Use verbos mensuráveis da Taxonomia de Bloom.
* Os objetivos devem aumentar progressivamente em complexidade cognitiva.
* Linguagem clara, técnica e mensurável.
* Os objetivos devem cobrir tanto fundamentos teóricos quanto implementação prática.
* Não invente campos extras.
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

match = re.search(r'disciplina\s+"([^"]+)"', prompt_objetivos)
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
