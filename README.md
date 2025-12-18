# Inteli - Instituto de Tecnologia e Liderança 

<p align="center">
<a href= "https://www.inteli.edu.br/"><img width="304" height="166" alt="Image" src="https://github.com/user-attachments/assets/c78ee6b1-b7bf-4498-b62f-1c9e0afed631" /></a>
</p>

# ChatBot para auxílio de pesquisa documental com linguagem natural

## Chatbofa

### Integrantes: 
- <a href="https://www.linkedin.com/in/erictach/">Eric Tachdjian</a>
- <a href="https://www.linkedin.com/in/gabriel-rocha-pinto-santos-/">Gabriel Rocha Pinto Santos</a>
- <a href="https://www.linkedin.com/in/pedromunhozsouza/">Pedro Munhoz de Souza Rivero</a>
- <a href="https://www.linkedin.com/in/rafael-moritz/">Rafael Lupovici Moritz</a>

## 📝 Descrição

O Bank of America é uma das principais instituições financeiras do mundo, atendendo indivíduos, pequenas e médias empresas, grandes corporações e governos com uma gama completa de produtos e serviços bancários, de gestão de investimentos e outros produtos e serviços financeiros e de gestão de risco. Atualmente, processos e procedimentos internos do Operations Brazil estão documentados em portais e repositórios internos, mas a busca por essas informações é pouco intuitiva e, muitas vezes, ineficiente. Os funcionários perdem tempo procurando manuais, fluxos e normas, além de não haver um mecanismo integrado que ofereça respostas atualizadas, adaptadas ao contexto de cada área e às regras de Compliance e Info Security. O objetivo é de desenvolver uma solução que permita a centralização e atualização de informações relacionadas a processos, acessos, treinamentos, normas e diretrizes que devem ser considerados por funcionários, permitindo a integração de diversas fontes e tipos de conteúdo. A solução envolve Chatbot corporativo que, com aplicação de tecnologias on-premises, permite a recuperação das informações previamente centralizadas e atualizadas por meio de consultas realizadas em linguagem natural.

## 📁 Estrutura de pastas

    /chatbot_project
    │
    ├── src/                     # Código-fonte principal da aplicação
    │   ├── api/                 # Lógica das APIs da aplicação
    │   │   └── main.py         
    │   │
    │   ├── core/                # Lógica central da arquitetura
    │   │   ├── __init__.py
    │   │   ├── embedder.py      # Módulo para o Modelo de Embedding Compartilhado
    │   │   ├── vectordb.py      # Módulo para interface com o Banco de Dados de Vetores (Qdrant)
    │   │   ├── generator.py     # Módulo para chamar o TGI do Hugging Face e acessar o LLM
    │   │   └── auth.py          # Módulo para segurança e autenticação
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
    ├── frontend/                  
    │   ├── app.py
    │
    ├── docs/                  # Documentações principais do projeto
    │   ├── apresentacoes/
    │   ├── img/
    │   ├── sprint 1/
    │   └── README.md
    │   └── manual_de_utilizacao
    │   └── testes
    │
    ├── requirements.txt       # Lista de dependências Python (bibliotecas)
    │
    ├── .gitignore             # Arquivos para ignorar no Git (venv, logs, etc.)
    │
    └── README.md              # Guia e explicação geral sobre o projeto

## 🔧 Instalação

As informações completas sobre a instalação do projeto, incluindo um passo a passo detalhado, dependências e versões utilizadas, podem ser encontradas no arquivo "docs/Manuais de Utilização/manual_de_utilizacao.md". Você pode acessar o documento através do seguinte link: <a href="https://github.com/Inteli-College/2025-2A-T22-G92-PUBLICO/blob/main/docs/Manuais%20de%20Utiliza%C3%A7%C3%A3o/manual_de_utilizacao.md" >manual de utilização</a>.

O arquivo fornecerá todas as informações necessárias para realizar a instalação e configuração correta do projeto, garantindo que você tenha todas as dependências corretas e versões adequadas para o funcionamento adequado do sistema.

## 🗃 Histórico de lançamentos


* 0.10.0 - 18/12/2025
    * Décima entrega: Tratar erros, lidar com ajuste de hiperparâmetros e finalizar a documentação
* 0.9.0 - 05/12/2025
    * Nona entrega: Aperfeiçoamento do front-end e do modelo de LLM
* 0.8.0 - 21/11/2025
    * Oitava entrega: Desenvolver a interface mínima (front-end) e fechar o fluxo de comunicação de ponta a ponta (MVP)
* 0.7.0 - 07/11/2025
    * Sétima entrega: Testar diferentes LLMs e desenvolver o template de prompt para o RAG, retornando a resposta gerada pelo LLM
* 0.6.0 - 24/10/2025
    * Sexta entrega: Criar POST para enviar a pergunta do usuário, usar o embedder para tranformar o texto em vetor e buscar os chunks mais relevantes no Qdrant, retornando os top-k valores mais próximos na API
* 0.5.0 - 10/10/2025
    * Quinta entrega: Aperfeiçoamento e leitura da vetorização por uma API
* 0.4.0 - 26/09/2025
    * Quarta entrega: Vetorização e salvamento dos dados no servidor local
* 0.3.0 - 12/09/2025
    * Terceira entrega: Início do processamento de dados do parceiro e definição de algoritmos
* 0.2.0 - 29/08/2025
    * Segunda entrega: Desenho da arquitetura do projeto (banco de dados, servidor local, ferramentas)
* 0.1.0 - 15/08/2025
    * Primeira entrega: Documentação do plano de projeto

	
## 📋 Licença/License

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/Inteli-College/2025-2A-T22-G92-PUBLICO">ChatBot para auxílio de pesquisa documental com linguagem natural</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://github.com/InteliProjects">Inteli</a>, Chatbofa: <a href="#">Eric Tachdjian</a>,  <a href="#">Gabriel Rocha Pinto Santos</a>,  <a href="#">Pedro Munhoz de Souza Rivero</a>, <a href="#">Rafael Lupovici Moritz</a>,
is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International <img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"></a></p>


## 🎓 Referências

[1] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing*, 2019. [Online]. Available: https://arxiv.org/abs/1908.10084  

[2] OpenAI, “Text Embedding Models,” *OpenAI Documentation*, 2024. [Online]. Available: https://platform.openai.com/docs/guides/embeddings  

[3] Cohere, “Embeddings,” *Cohere Documentation*, 2024. [Online]. Available: https://docs.cohere.com/docs/embeddings  

[4] J. Wang, Y. Kuo, and D. Zhou, “Text Embeddings by Weakly-Supervised Contrastive Pre-training,” *arXiv preprint arXiv:2212.03533*, 2022. [Online]. Available: https://arxiv.org/abs/2212.03533  

[5] Hugging Face, “SentenceTransformers Documentation,” *Hugging Face*, 2024. [Online]. Available: https://www.sbert.net/  

[6] LangChain, “Text Splitters,” *LangChain Documentation*, 2024. [Online]. Available: https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/ 
