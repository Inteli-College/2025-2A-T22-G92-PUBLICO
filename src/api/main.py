import os
import shutil
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from ..ingestion.process_pdf_url import process_pdf, process_url, process_batch_urls
from ..ingestion.qdrant_config import get_qdrant_client, COLLECTION_NAME

app = FastAPI(title="Bank of America PDF Upload API")
qdrant_client = get_qdrant_client()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class URLPayload(BaseModel):
    url: str
    
class BatchURLPayload(BaseModel):
    urls: list[str]
    
@app.get("/")
def read_root():
    """
    Endpoint genérico para verificar se o get está funcional.
    """
    return {"message": "API rodando. Use /upload-pdf para enviar PDFs."}

@app.get("/ingest/test")
def test_qdrant_connection():
    """
    Endpoint de teste para verificar se a conexão com o Qdrant está funcionando e
    quantos documentos existem na coleção.
    """
    try:
        count_result = qdrant_client.count(collection_name=COLLECTION_NAME, exact=True)
        
        return {
            "status": "sucesso",
            "message": "Conexão com Qdrant estabelecida.",
            "collection_name": COLLECTION_NAME,
            "total_documents": count_result.count,
            "saude": "OK"
        }
    except Exception as e:
        return {
            "status": "erro",
            "message": "Falha ao conectar ou contar documentos no Qdrant.",
            "detalhe": str(e),
            "saude": "ERRO"
        }

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint de envio de PDF únicos, de forma que o conteúdo seja extraído, normalizado,
    separado em chunkings, convertido em embeddings e, por fim, salvo no banco Qdrant.
    """
    if not file.filename.endswith(".pdf"):
        return {"error": "Apenas arquivos PDF são aceitos."}
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)            
        process_pdf(file_path, source_url=file.filename)
        
    except Exception as e:
        return {"status": "erro", "detalhe": f"Falha no processamento: {e}"}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            
    return {"status": "sucesso", "arquivo": file.filename, "chunks_adicionados": "Verifique o log."}

@app.post("/upload-url")
async def upload_url(payload: URLPayload):
    """
    Endpoint de envio de URL únicas, de forma que o conteúdo seja convertido para PDF, extraído,
    normalizado, separado em chunkings, convertido em embeddings e, por fim, salvo no banco Qdrant.
    """
    url = payload.url
    
    if not url.strip():
        return {"error": "A URL fornecida está vazia."}

    file_name = process_url(url)
    
    if file_name:
        return {
            "status": "sucesso", 
            "url": url, 
            "mensagem": f"Documento da URL {url} processado e salvo no VectorDB."
        }
    else:
        return {
            "status": "erro", 
            "url": url, 
            "mensagem": "Falha ao baixar, extrair ou processar a URL. Verifique os logs."
        }

@app.post("/ingest/batch")
async def ingest_url_batch(payload: BatchURLPayload):
    """
    Endpoint de envio de URL em batch, de forma que o conteúdo seja convertido para PDF, extraído,
    normalizado, separado em chunkings, convertido em embeddings e, por fim, salvo no banco Qdrant.
    """
    urls_list = payload.urls
    
    if not urls_list:
        return {"error": "A lista de URLs está vazia.", "status": "erro"}
    
    print(f"Recebida requisição de lote com {len(urls_list)} URLs.")
    
    try:
        total_chunks = await run_in_threadpool(process_batch_urls, urls_list)
        
        return {
            "status": "processamento_iniciado",
            "total_urls_recebidas": len(urls_list),
            "total_chunks_processados": total_chunks,
            "mensagem": "O processamento em lote foi concluído em background.",
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": "Falha durante a execução do processo em lote.",
            "detalhe": str(e)
        }
