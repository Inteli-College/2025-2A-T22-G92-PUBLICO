import os
import uuid
import tempfile
from datetime import datetime
from PyPDF2 import PdfReader
from qdrant_client.http.models import PointStruct
from .qdrant_config import get_qdrant_client
from .parser import extract_text_from_local_pdf 
from ..core.embedder import Embedder 
from .normalizer import normalize_text
from .scraper import url_to_local_pdf

# Inicializações de instâncias
qdrant_client = get_qdrant_client()
embedder = Embedder() # Instancia o Embedder uma vez (carrega o modelo SBERT)
COLLECTION_NAME = "bofa_documents"

def process_pdf(file_path: str, source_url: str):
    """ 
    Orquestra a ingestão de um único arquivo PDF, reusando os componentes
    do pipeline principal (extração, normalização, chunking, embedding).
    """
    # 1. EXTRAÇÃO (Parser)
    raw_text = extract_text_from_local_pdf(file_path)
    if not raw_text:
        print(f"[PROCESS PDF] Nenhum texto extraído de {file_path}. Abortando.")
        return
    
    # 2. NORMALIZAÇÃO (Normalizer)
    clean_text = normalize_text(raw_text)
    if not clean_text:
        print(f"[PROCESS PDF] Texto normalizado vazio. Abortando.")
        return
    
    # 3. CHUNKING (Embedder)
    # Usa o método chunk_text da instância Embedder
    chunks = list(embedder.chunk_text(clean_text))
    if not chunks:
        print(f"[PROCESS PDF] Nenhum chunk gerado. Abortando.")
        return
    
    # 4. EMBEDDING (Embedder)
    # Usa o método embed da instância Embedder. Converte para list para o Qdrant.
    embeddings = embedder.embed(chunks).tolist()
    
    # 5. MONTAGEM E PERSISTÊNCIA NO QDRANT
    current_timestamp = datetime.now().isoformat(timespec='milliseconds')
    
    points = []
    
    for i in range(len(chunks)):
        unique_point_id = str(uuid.uuid4())        
        points.append(
            PointStruct(
                id=unique_point_id,
                vector=embeddings[i],
                payload={
                    "chunk": chunks[i],
                    "source": source_url, 
                    "chunk_index": i + 1, 
                    "last_updated": current_timestamp,
                }
            )
        )
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"[PROCESS_PDF_URL] {len(points)} chunks do arquivo {source_url} processados e adicionados")

def process_url(url: str) -> str | None:
    """
    Baixa o PDF de uma URL, processa-o e limpa o arquivo temporário.
    Retorna o nome do arquivo se bem-sucedido.
    """
    
    # Define um local temporário para salvar o arquivo baixado e cria um diretório temporário para ser seguro
    temp_dir = tempfile.mkdtemp()
    local_pdf_path = None
    
    try:
        # 1. AQUISIÇÃO/SCRAPING: Baixa o PDF para o disco local
        print(f"[PROCESS URL] Tentando baixar {url}...")
        local_pdf_path = url_to_local_pdf(url, temp_dir)
        
        if local_pdf_path:
            # 2. PROCESSAMENTO: Chama a função que processa o arquivo local
            file_name = os.path.basename(local_pdf_path)
            process_pdf(file_path=local_pdf_path, source_url=url)
            return file_name
        else:
            print(f"[PROCESS URL] Falha na aquisição da URL: {url}")
            return None
            
    except Exception as e:
        print(f"[PROCESS URL] Erro ao processar URL {url}: {e}")
        return None
    
    finally:
        # 3. LIMPEZA: Remove o diretório temporário e seu conteúdo
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            
def process_batch_urls(urls_list: list[str]) -> int:
    """
    Executa o pipeline de ingestão para uma lista de URLs fornecida (lote).
    Ele faz o scraping, extração, normalização, chunking, embedding e
    um upsert BULK no Qdrant.
    Retorna o número de chunks processados.
    """
    if not urls_list:
        print("[BATCH] Nenhuma URL para processar.")
        return 0

    print(f"[BATCH] Iniciando processamento em lote de {len(urls_list)} URLs...")
    
    all_chunks_for_db = []
    
    # O timestamp é o mesmo para todo o lote, para rastreamento
    current_timestamp_full = datetime.now().isoformat(timespec='milliseconds')
    
    # Cria um diretório temporário para ser seguro no processamento do lote
    with tempfile.TemporaryDirectory() as temp_dir:
        
        for idx, url in enumerate(urls_list, start=1):
            local_pdf_path = None
            print(f"  ({idx}/{len(urls_list)}) Processando URL: {url}")
            
            try:
                # AQUISIÇÃO/SCRAPING: Baixa o PDF para o diretório temporário
                local_pdf_path = url_to_local_pdf(url, temp_dir)
                
                if not local_pdf_path:
                    print(f"  [ERRO] Falha na aquisição (URL não retornou PDF) para: {url}")
                    continue
                
                # EXTRAÇÃO: extrai o conteúdo de cada URL
                extracted_text = extract_text_from_local_pdf(local_pdf_path)
                
                # NORMALIZAÇÃO
                normalized_text = normalize_text(extracted_text)
                
                # CHUNKING (usa o método do Embedder global)
                chunk_texts = list(embedder.chunk_text(normalized_text))
                
                if not chunk_texts:
                    print(f"  [AVISO] Nenhum chunk gerado para {url}. Pulando.")
                    continue
                
                # EMBEDDING
                embeddings = embedder.embed(chunk_texts).tolist()
                
                # MONTAGEM: Adiciona todos os chunks à lista de lote
                for i, chunk in enumerate(chunk_texts):
                    unique_point_id = str(uuid.uuid4())
                    
                    all_chunks_for_db.append(
                        PointStruct(
                            id=unique_point_id,
                            vector=embeddings[i],
                            payload={
                                "chunk": chunk,
                                "source": url,
                                "chunk_index": i + 1,
                                "last_updated": current_timestamp_full,
                            }
                        )
                    )
                
            except Exception as e:
                print(f"  [ERRO GRAVE] Falha interna no processamento de {url}: {e}")
                            
    # PERSISTÊNCIA: Upsert único (bulk) no Qdrant
    if all_chunks_for_db:
        print(f"[BATCH] Iniciando upsert de {len(all_chunks_for_db)} chunks no Qdrant...")
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=all_chunks_for_db)
        print(f"[BATCH] Upsert concluído com sucesso.")
        return len(all_chunks_for_db)
        
    return 0
            