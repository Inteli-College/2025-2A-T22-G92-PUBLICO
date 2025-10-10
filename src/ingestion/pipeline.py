import os
import json
import hashlib
import uuid
from .scraper import url_to_local_pdf
from .parser import extract_text_from_local_pdf
from .normalizer import normalize_text
from ..core.embedder import Embedder
from ..core.vectordb import VectorDB
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

LOCAL_PDFS_DIR = os.path.join(RAW_DATA_DIR, 'temp_pdfs') 
URLS_FILE_PATH = os.path.join(RAW_DATA_DIR, 'urls.txt')
SCRAPED_OUTPUT_FILE = os.path.join(PROCESSED_DATA_DIR, 'scraped_data.json')
NORMALIZED_OUTPUT_FILE = os.path.join(PROCESSED_DATA_DIR, 'normalized_data.json')

def run_ingestion_pipeline():
    """
    Executa o pipeline de ingestão de dados:
      1. Lê as URLs do arquivo urls.txt
      2. Faz scraping ou extração de PDFs
      3. Gera embeddings
      4. Salva em JSON
      5. Armazena os embeddings no Qdrant
    """
    print("Iniciando o pipeline de ingestão de dados...")
    
    try:
        with open(URLS_FILE_PATH, 'r', encoding='utf-8') as f:
            urls_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo de URLs não encontrado em {URLS_FILE_PATH}. Pipeline encerrado.")
        return

    if not urls_list:
        print("Nenhuma URL encontrada. Pipeline encerrado.")
        return

    print(f"{len(urls_list)} URLs carregadas do arquivo.")
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(LOCAL_PDFS_DIR, exist_ok=True) 

    embedder = Embedder()
    vectordb = VectorDB()
    all_chunks_for_db  = []
    
    # Verifica a dimensão do embedding
    embedding_dim = embedder.model.get_sentence_embedding_dimension()
    
    # Obtem o timestamp exato de quando o documento está sendo processado, para garantir que todos os chunks do mesmo documento tenham a mesma data de processamento.
    current_timestamp_full = datetime.now().isoformat(timespec='milliseconds')
       
    # Será usado o timestamp original (com caracteres) para o metadado (payload)
    current_timestamp_for_payload = current_timestamp_full 

    for idx, url in enumerate(urls_list, start=1):
        print(f"\n({idx}/{len(urls_list)}) Processando: {url}")
        
        local_pdf_path = None
        
        try:
            # AQUISIÇÃO/CONVERSÃO: Garante que existe um PDF local
            local_pdf_path = url_to_local_pdf(url, LOCAL_PDFS_DIR)
        
        except Exception as e:
            print(f"[PIPELINE][ERRO DE AQUISIÇÃO] Falha ao converter/baixar {url}: {e}")
            continue

        if local_pdf_path:
            # EXTRAÇÃO: Usa a função de extração que só lida com arquivos locais
            extracted_text = extract_text_from_local_pdf(local_pdf_path)
            
            # COMENTAR ESSA PARTE PARA VISUALIZAR OS PDFs TEMPORÁRIOS
            # Limpeza do arquivo temporário 
            try:
                os.remove(local_pdf_path)
            except Exception as e:
                print(f"[PIPELINE] Aviso: Não foi possível remover arquivo temp {local_pdf_path}. {e}")
        
            if extracted_text:
                # Passo de Normalização (limpa o texto)
                normalized_text = normalize_text(extracted_text)
                if not normalized_text:
                    print(f"[PIPELINE] Texto normalizado vazio para {url}. Pulando.")
                    continue
                
                # Chunking (usa o texto já limpo/normalizado e o divide)
                chunk_texts = list(embedder.chunk_text(normalized_text))
                if not chunk_texts:
                    print(f"[PIPELINE] Documento extraído, mas nenhum chunk gerado para {url}. Pulando.")
                    continue
                
                # Geração de Embedding (usando o texto normalizado e em chunks)
                embeddings = embedder.embed(chunk_texts)
                
                print(f"[PIPELINE] Texto normalizado com {len(chunk_texts)} chunks. Embeddings gerados ({embedding_dim} dimensões).")
            
                # Inserção na lista final
                for i, chunk in enumerate(chunk_texts):
                    # Gera o ID único temporal
                    unique_point_id = str(uuid.uuid4())
                    
                    all_chunks_for_db.append({
                        "point_id": unique_point_id,
                        "chunk": chunk,
                        "source": url,
                        "chunk_index": i + 1, # importante para contexto: retornar os chunks em volta
                        "last_updated": current_timestamp_for_payload,
                        "embedding": embeddings[i].tolist() 
                    })
            else:
                print(f"[PIPELINE][ERRO] Nenhum texto retornado de {url}")
        else:
            print(f"[PIPELINE] Falha na aquisição (sem arquivo PDF local) para {url}.")

    if not all_chunks_for_db :
        print("[PIPELINE][ERRO] Nenhum conteúdo foi processado. Pipeline encerrado.")
        return

    # Geração dos arquivos JSON
    
    # Geração do arquivo 'scraped_data.json' (Com embeddings)
    with open(SCRAPED_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks_for_db , f, ensure_ascii=False, indent=4)
    print(f"\nDados processados (com embedding) salvos em: {SCRAPED_OUTPUT_FILE} ({len(all_chunks_for_db )} chunks)")

    # Geração do arquivo 'normalized_data.json' (Apenas texto e fonte)
    normalized_data_only = [{
        "chunk": item["chunk"],
        "source": item["source"],
        "last_updated": item["last_updated"]
    } for item in all_chunks_for_db ]
    
    with open(NORMALIZED_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(normalized_data_only, f, ensure_ascii=False, indent=4)
    print(f"Dados normalizados (texto e fonte) salvos em: {NORMALIZED_OUTPUT_FILE} ({len(normalized_data_only)} chunks)")
    
    # Armazenamento no Qdrant - banco vetorial
    print("[PIPELINE] Salvando os dados no Qdrant...")
    vectordb.add_documents(all_chunks_for_db)
    count = vectordb.client.count(collection_name="documents").count
    print(f"[PIPELINE] Total de documentos salvos no Qdrant: {count}")

    # print("\nExemplo de documento processado:")
    # print(json.dumps(all_chunks_for_db[0], ensure_ascii=False, indent=2))
 
    print("\nPipeline concluído (PDF + HTML + Normalização + Chunking + embeddings + Qdrant).")

if __name__ == "__main__":
    run_ingestion_pipeline()