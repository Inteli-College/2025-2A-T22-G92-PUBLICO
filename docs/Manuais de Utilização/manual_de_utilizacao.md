# Manual de Utilização — Projeto RAG BOFA

Este manual descreve **como utilizar o projeto como um todo**, partindo do princípio de que o sistema é executado via **Docker** e que o usuário **não precisa rodar o Streamlit manualmente**. Após a inicialização, o front-end fica disponível diretamente via navegador, através de um endereço `localhost`.

---

## Pré-requisitos

Antes de iniciar, é necessário que o ambiente possua:

* Docker Desktop instalado e em execução
* Docker Compose habilitado
* Git instalado

> Não é necessário instalar Python nem Streamlit localmente para utilização do sistema.

---

## Estrutura do Projeto

Após clonar o repositório, a estrutura principal do projeto será semelhante a:

```
/projeto
 ├── backend/
 ├── frontend/
 ├── docker-compose.yml
 ├── .env
 └── README.md
```

O front-end (Streamlit), o back-end (API RAG) e os demais serviços são executados **exclusivamente via Docker**.

---

## Configuração Inicial (.env)

Antes de subir o projeto, é necessário criar um arquivo `.env` na **raiz do projeto** com as seguintes variáveis:

```
SECRET_KEY=PEDORIH4FGSJVK12342KJLNDORA53647UYT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Este arquivo é local e não deve ser versionado.

---

## Subindo o Projeto

Com o Docker Desktop aberto, execute o comando abaixo na **raiz do projeto**:

```bash
docker-compose up --build -d
```

Esse comando irá:

* Construir as imagens necessárias
* Subir o back-end
* Subir o front-end
* Inicializar os serviços auxiliares

Após a execução bem-sucedida, o sistema estará pronto para uso.

---

## Acessando o Sistema

Com os containers em execução, basta abrir o navegador e acessar:

```
http://localhost:8501
```

Não é necessário rodar nenhum comando adicional.

---

## Autenticação

Ao acessar o sistema, será exibida a tela de login.

Usuários disponíveis:

* `admin`
* `gerente`
* `analista`
* `aluno`

Senha (para todos os usuários):

```
admin
```

Após autenticação, o usuário passa a ter acesso às funcionalidades de acordo com seu cargo.

---

## Funcionalidades do Sistema

O sistema é dividido em duas grandes áreas:

### 1. Upload de Material

A área de ingestão permite adicionar conteúdos que serão utilizados pelo mecanismo RAG.

Ela é composta por três abas:

#### a) Upload de PDF

* Permite enviar arquivos PDF via upload
* É obrigatório definir quais cargos podem acessar o documento
* O conteúdo é processado e indexado automaticamente

#### b) URL Única

* Permite inserir uma única URL por vez
* O conteúdo da página é coletado e indexado
* É possível definir os cargos autorizados

#### c) Batch de URLs

* Permite inserir múltiplas URLs (uma por linha)
* Todas as URLs são processadas em lote
* O controle de acesso é aplicado ao conjunto

Em todas as opções, é necessário confirmar a ação clicando no botão correspondente.

---

### 2. Chat / Perguntas (RAG)

A aba de consulta é a funcionalidade central do projeto.

Nela, o usuário pode:

* Digitar perguntas em linguagem natural
* Consultar apenas documentos compatíveis com seu cargo
* Receber respostas geradas pelo modelo RAG

Além da resposta principal, o sistema exibe:

* As fontes utilizadas
* Os trechos (chunks) recuperados
* Metadados como relevância e data de atualização

Isso garante **transparência e rastreabilidade da resposta**.

---

## Encerrando o Sistema

Para parar completamente o projeto, utilize:

```bash
docker-compose down
```

Isso encerrará todos os containers de forma segura.

---

## Considerações Finais

* Todo o uso do sistema ocorre via navegador
* Nenhum comando adicional é necessário após o `docker-compose up`
* O controle de acesso por cargo é aplicado tanto na ingestão quanto na consulta
* O projeto está preparado para demonstrações, apresentações e avaliação acadêmica

---
