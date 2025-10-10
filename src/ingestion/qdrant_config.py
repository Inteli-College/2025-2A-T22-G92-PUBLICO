from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PayloadSchemaType

COLLECTION_NAME = "bofa_documents"
VECTOR_SIZE = 384

def get_qdrant_client():
    client = QdrantClient(host="localhost", port=6333)

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
        print(f"Coleção '{COLLECTION_NAME}' criada e indexada.")

    return client
