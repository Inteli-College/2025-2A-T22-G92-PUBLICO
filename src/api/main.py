import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, APIRouter, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from ..ingestion.process_pdf_url import process_pdf, process_url, process_batch_urls
from ..chatbot.retriever import retrieve_relevant_chunks
from ..ingestion.qdrant_config import get_qdrant_client, COLLECTION_NAME
from ..core.embedder import Embedder
from ..core.vectordb import VectorDB
from ..core.generator import generator
from ..core.auth import Token, create_access_token, get_current_active_user, User, fake_users_db, verify_password, get_user, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import Optional
from datetime import timedelta

qdrant_client = get_qdrant_client()

app = FastAPI(title="Bank of America PDF Upload API")

# Monta a pasta de arquivos para serem acessíveis via URL
app.mount("/files", StaticFiles(directory="/app/storage"), name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://127.0.0.1:5500"] para restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_embedder = Embedder()
app_vectordb: VectorDB = None

STORAGE_DIR = "/app/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

router = APIRouter()

# Essencial para não dar problema de conexão na inicialização do qdrant
@app.on_event("startup")
async def startup_event():
    global app_vectordb
    
    # A conexão e criação/verificação da coleção só ocorrem AQUI
    # O Uvicorn espera isso terminar antes de abrir a porta 8000
    print("[STARTUP] Inicializando conexão com VectorDB...")
    try:
        app_vectordb = VectorDB(collection_name=COLLECTION_NAME)
        print("[STARTUP] Conexão com VectorDB estabelecida e coleção verificada.")
    except Exception as e:
        # Se falhar aqui, o Uvicorn NÃO VAI subir. O erro será explícito.
        print(f"[STARTUP ERROR] Falha ao conectar ao Qdrant: {e}")
        raise

class URLPayload(BaseModel):
    url: str
    allowed_roles: list[str] = ["admin"]
    
class BatchURLPayload(BaseModel):
    urls: list[str]
    allowed_roles: list[str] = ["admin"]

class QueryRequest(BaseModel):
    query: str

class ChunkResponse(BaseModel):
    id: str | int
    score: float
    chunk: str
    source: str
    chunk_index: Optional[int] = None
    last_updated: str | None = None
    
@app.get("/")
def read_root():
    """
    Endpoint genérico para verificar se o get está funcional.
    """
    return {"message": "API rodando. Use http://127.0.0.1:8000/docs#/ para acessar o Swagger."}

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
async def upload_pdf(file: UploadFile = File(...), roles_csv: str = Form(default="admin", description="Cargos separados por vírgula (ex: admin, gerente)")):
    """
    Endpoint de envio de PDF únicos, de forma que o conteúdo seja extraído, normalizado,
    separado em chunkings, convertido em embeddings e, por fim, salvo no banco Qdrant.
    """
    if not file.filename.endswith(".pdf"):
        return {"error": "Apenas arquivos PDF são aceitos."}
    
    file_name = file.filename

    # Cria um nome único com UUID para salvar no disco, garantindo a exclusividade
    file_extension = file_name.split('.')[-1]
    unique_file_name_on_disk = f"{uuid.uuid4()}.{file_extension}"

    file_path = os.path.join(STORAGE_DIR, unique_file_name_on_disk)
    
    allowed_roles = [role.strip() for role in roles_csv.split(",")]
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)    

        # O link deve usar o nome único para que o FastAPI encontre no disco
        local_link = f"/files/{unique_file_name_on_disk}" 

        process_pdf(
            file_path=file_path,
            source_url=local_link,
            file_name_in_storage=unique_file_name_on_disk,
            display_name=file_name,
            embedder=app_embedder,
            allowed_roles=allowed_roles
        )
        
    except Exception as e:
        print(f"Erro no processamento de {file_name}: {e}")
        return {"status": "erro", "detalhe": f"Falha no processamento: {e}"}
            
    return {"status": "sucesso", "arquivo_salvo": unique_file_name_on_disk, "nome_original": file_name, "chunks_adicionados": "Verifique o log."}

@app.post("/upload-url")
async def upload_url(payload: URLPayload):
    """
    Endpoint de envio de URL únicas, de forma que o conteúdo seja convertido para PDF, extraído,
    normalizado, separado em chunkings, convertido em embeddings e, por fim, salvo no banco Qdrant.
    """
    url = payload.url
    
    if not url.strip():
        return {"error": "A URL fornecida está vazia."}

    file_name = await run_in_threadpool(
        process_url, 
        url, 
        app_embedder,
        payload.allowed_roles,
    )
    
    if file_name:
        return {
            "status": "sucesso", 
            "url": url, 
            "mensagem": f"Documento da URL {url} processado e salvo no Qdrant."
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
        total_chunks = await run_in_threadpool(
            process_batch_urls,
            urls_list,
            app_embedder,
            payload.allowed_roles
        )
        
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

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Rota de login para gerar o token de acesso e simular o login de uma role de acesso específica.
    """
    # Tenta buscar o usuário
    user = get_user(fake_users_db, form_data.username)
    
    # Valida senha
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Cria o token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, # Adiciona a role no token!
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/query")
async def handle_query(request: QueryRequest, current_user: User = Depends(get_current_active_user)):
    """
    Recebe uma pergunta (query) e o cargo do usuário (autenticação), busca no VectorDB aplicando o filtro de segurança e retorna os chunks de texto mais relevantes.
    """
    try:
        # Sobrescreve a role enviada no JSON pela role real do token (segurança)
        real_role = current_user.role
        print(f"DEBUG: Usuário {current_user.username} (Role: {real_role}) fez uma query.")

        top_results = retrieve_relevant_chunks(
            query=request.query,
            embedder=app_embedder,
            vectordb=app_vectordb,
            user_role=real_role,
        )
        # Formata o contexto final para o LLM
        formatted_context = "\n\n---\n\n".join([c['chunk'] for c in top_results])
        print(f"DEBUG: Contexto fornecido ao LLM:\n{formatted_context}")

        # Geração da Resposta
        try:
            final_answer = await generator.generate_response(
                contexto=formatted_context,
                pergunta=request.query
            )
        except Exception as e:
            print(f"Erro inesperado no handle_query: {e}")
            raise HTTPException(status_code=500, detail=f"Falha na geração da resposta pelo LLM: {e}")
    except ValueError as e:
        raise HTTPException(
            status_code=404, # Not found
            detail=str(e) # A mensagem do ValueError será o detalhe do erro
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno inesperado no servidor: {e}")

    # Retorna a resposta (final_answer) e os chunks originais (top_results)
    return {
        "answer": final_answer,
        "chunks": top_results
    }

app.include_router(router)
