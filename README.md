# 2025-2A-T21-G92-INTERNO
Repository for group 92 of class T21 (2025/2A)

## Estrutura de Pastas e Arquivos

    /chatbot_project
    │
    ├── data/                    # Fontes de dados brutos
    │   ├── raw/                 # Documentos e arquivos brutos
    │   │   ├── docs/
    │   │   ├── scraped_data.json
    │   │   └── urls.txt
    │
    ├── src/                     # Código-fonte principal da aplicação
    │   ├── api/                 # Lógica das APIs da aplicação
    │   │   └── main.py         
    │   │
    │   ├── core/                # Lógica central da arquitetura
    │   │   ├── __init__.py
    │   │   ├── embedder.py      # Módulo para o Modelo de Embedding Compartilhado
    │   │   └── vectordb.py      # Módulo para interface com o Banco de Dados de Vetores (Qdrant)
    │   │
    │   ├── ingestion/           # Módulo para o Fluxo de Ingestão de Dados
    │   │   ├── __init__.py
    │   │   ├── normalizer       # Lógica para limpar o texto cru do Scraping
    │   │   ├── scraper.py       # Lógica do Web Scraper que converte URLs para PDF
    │   │   ├── parser.py        # Lógica da extração de texto dos PDFs
    │   │   └── pipeline.py      # Orquestra os passos de ingestão
    |   |   └── qdrant_config.py # Configura o banco Qdrant para a ingestão via API
    |   |   └── process_pdf_url.py # Processa o PDF e as URLS na API
    │   │
    │   ├── chatbot/             # Módulo para o Fluxo de Consulta do Usuário
    │   │   ├── __init__.py
    │   │   ├── llm_model.py     # Interface com o Modelo de Geração (LLM)
    │   │   ├── backend.py       # Lógica do Backend (Orquestrador)
    │   │   └── api.py           # Endpoints da API (Flask/FastAPI)
    │   │
    │   └── main.py              # Ponto de entrada da aplicação
    │
    ├── tests/                   # Testes unitários e de integração
    │   ├── test_ingestion.py  
    │   ├── test_scraper.py
    │   └── test_chatbot.py
    │
    ├── docs/                  # Documentações principais do projeto
    │   ├── apresentacoes/
    │   ├── img/
    │   ├── sprint 1/
    │   └── README.md
    │   └── manual_de_utilizacao
    │
    ├── requirements.txt       # Lista de dependências Python (bibliotecas)
    │
    ├── .gitignore             # Arquivos para ignorar no Git (venv, logs, etc.)
    │
    └── README.md              # Instruções de pastas do repositório
