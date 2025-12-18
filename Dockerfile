# Imagem Base: imagem leve do Python
FROM python:3.11-slim

# Configurações de Ambiente
# Evita arquivos .pyc e buffer no stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
    
# Define o diretório de trabalho dentro do container
WORKDIR /app

# Para ser possível relizar o Web Scraping
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente para o Python saber onde estão os binários do sistema    
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER_PATH=/usr/bin/chromedriver

# Cria armazenamento para PDFs
RUN mkdir -p /app/storage && chmod 777 /app/storage

# Copia Requisitos e Instala Dependências
COPY requirements.txt /app/

# Instala todas as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação para o diretório de trabalho
COPY ./src /app/src

# Procura pacotes dentro de /app/src
ENV PYTHONPATH=/app/src

# Expõe a Porta da Aplicação (porta que o Uvicorn vai escutar)
EXPOSE 8000

# Inicializa e roda a aplicação usando Uvicorn (servidor ASGI)
# O host 0.0.0.0 garante que o container escute em todas as interfaces de rede.
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]