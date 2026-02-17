# Projeto IC XPE 2026

Este projeto foi reorganizado seguindo a estrutura padrão de projetos de ciência de dados.

## Estrutura do Projeto

```text
├── README.md          <- Este arquivo
├── data
│   ├── processed      <- Conjuntos de dados finais (Rankings em csv)
│   └── raw            <- Dados originais imutáveis (Objetivos e Projetos em .json)
├── docs               <- Documentação do projeto
├── models             <- Modelos de I.A listados
├── pyproject.toml     <- Configuração do projeto e metadados
├── references         <- Dicionários de dados e manuais
├── requirements.txt   <- Arquivo de dependências
├── setup.cfg          <- Configuração para flake8
└── src                <- Código fonte do projeto 
    ├── generateobjectives.py     <- Script para gerar objetivos
    ├── generatePBL.py    <- Script para gerar PBL 
    ├── rank_obj_projects.py   <- Script de ranking   
```

## Como Usar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure suas variáveis de ambiente no arquivo `.env`.

3. Antes de executar o generateobjectives.py, acesse-o e altere o trecho a partir da palavra disciplina para definir o que quer gerar

prompt_objetivos = """
Gere 50 objetivos de aprendizagem para a disciplina `Aprendendo Javascript.`


4. Antes de executar o generatePBL.py, acesse-o e altere o trecho abaixo, a partir da palavra disciplina para definir o que quer gerar.

prompt_pbl = """
Gere 50 projetos PBL (Project-Based Learning) para a disciplina `Aprendendo Javascript`.

Mova ambos os arquivos .txt gerados na pasta para raw

5. Execute rank_obj_projects.py

o resultado aparecerá na pasta processed.


