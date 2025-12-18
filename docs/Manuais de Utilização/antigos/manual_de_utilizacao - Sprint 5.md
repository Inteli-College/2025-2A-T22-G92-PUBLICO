# Manual de Utilização — Servidor Local, API de Ingestão (Qdrant + FastAPI)

Este manual explica **como rodar todo o projeto localmente**, incluindo o servidor Qdrant, a API FastAPI de ingestão de dados, e como verificar o sucesso da vetorização. O objetivo é permitir que qualquer pessoa consiga reproduzir o funcionamento completo apenas seguindo este passo a passo, e adicionando suas prints onde indicado.

## Pré-requisitos

- Python 3.10+
- Docker
- Git

## Instalação das Dependências

```bash
pip install -r requirements.txt
```

## Rodando o Banco Vetorial (Qdrant) Localmente:

```bash
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

```bash
$env:QDRANT_HOST="127.0.0.1"
$env:QDRANT_PORT="6333"
```

<img width="1138" height="141" alt="image" src="https://github.com/user-attachments/assets/9189c987-40e9-4330-b4ca-1ff4dc0135f4" />

Acesse o localhost para verificar: http://localhost:6333/

## Servidor Remoto

Se o Qdrant estiver em um servidor remoto:

No Terminal:

```bash
$env:QDRANT_HOST = "XX.XXX.X.XX"   # IP do servidor remoto
$env:QDRANT_PORT = "6333"          # Porta do Qdrant
```

## Rodando a API de Ingestão (FastAPI)

```Bash
uvicorn src.api.main:app --reload
```

<img width="729" height="96" alt="image" src="https://github.com/user-attachments/assets/08ec4fc1-fd66-470b-b394-6b7e69b0c800" />

Acesse no navegador: http://127.0.0.1:8000

Você deve ver:
<img width="867" height="188" alt="image" src="https://github.com/user-attachments/assets/70c7a836-105d-483d-b3da-b7c0abe171cf" />

Verificar utilizando no powershell:
```bash
Invoke-WebRequest -Uri "http://127.0.0.1:8000/ingest/test" -Method GET
```

<img width="1431" height="513" alt="image" src="https://github.com/user-attachments/assets/e5fe56da-9dcb-49b3-8174-7d3dcf141632" />

## Realizando a Ingestão de Dados

Com URLs - Exemplo do site do Banco Central Brasileiro

No powershell
```bash
$urls = @{
    "urls" = @(
        "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=5237",
        "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=5238",
        "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=453"
    )
}

Invoke-WebRequest -Uri "http://127.0.0.1:8000/ingest" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body ($urls | ConvertTo-Json -Depth 5)
```

Resultado
<img width="1388" height="547" alt="image" src="https://github.com/user-attachments/assets/3aab0b4f-7d8c-4ede-aba2-baebad612c81" />

É possivel verificar se foi salvo no localhost
http://localhost:6333/collections/documents/points/#idDoItem (1,2,3, etc...)

<img width="1916" height="700" alt="image" src="https://github.com/user-attachments/assets/cd433a19-f8a7-4086-a98a-7ba33be85bbb" />

## Rodando a API de PDF (upload-pdf)

```Bash
uvicorn src.api.main:app --reload
```

Acesse no navegador: http://127.0.0.1:8000/docs

Você deve ver:
<img width="1892" height="567" alt="Image" src="https://github.com/user-attachments/assets/cd5976c6-1c85-4f73-a36a-ad22fe2e4567" />

Procure pelo endpoint Post \upload-pdf e em seguida aperte "Try it ouy":
<img width="1919" height="411" alt="Image" src="https://github.com/user-attachments/assets/725bf417-0778-4c6b-b852-9f5181acbb9c" />

Selecione o PDF desejado e execute:
<img width="1918" height="825" alt="Image" src="https://github.com/user-attachments/assets/e6d55d6f-c651-4b1b-b933-c7bcf8b99f16" />

então você poderá ver o resultado, deve ver algo como:
<img width="1907" height="894" alt="Image" src="https://github.com/user-attachments/assets/fa301848-0b70-43aa-b388-ff6d9c7ed4c0" />
