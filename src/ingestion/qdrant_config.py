from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PayloadSchemaType
import os
import time

COLLECTION_NAME = "bofa_documents"
VECTOR_SIZE = 384

def get_qdrant_client():
    client = QdrantClient(host="qdrant", port=6333)
    url = os.getenv("QDRANT_URL", "http://localhost:6333")

    for attempt in range(20):
        try:
            client = QdrantClient(url=url)
            client.get_collections()  # teste simples
            return client
        except Exception:
            print(f"Qdrant não está pronto. Tentativa {attempt+1}/20...")
            time.sleep(2)

    raise RuntimeError("Qdrant não respondeu após múltiplas tentativas.")
    try:
        client.get_collection(collection_name=COLLECTION_NAME)
        print(f"Coleção '{COLLECTION_NAME}' já existe.")
    
    except Exception:
        print(f"Coleção '{COLLECTION_NAME}' não encontrada. Criando...")
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="last_updated",
            field_schema=PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="allowed_roles",
            field_schema=PayloadSchemaType.KEYWORD 
        )
        print(f"Coleção '{COLLECTION_NAME}' criada e indexada.")

    return client
