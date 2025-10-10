import os
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    PointStruct,
    Distance,
    PayloadSchemaType
)

class VectorDB:
    def __init__(self, 
                 host=None, 
                 port=None, 
                 collection_name="documents", 
                 vector_size=384):
        """
        Inicializa o cliente Qdrant e garante que a coleção esteja criada.
        O host e a porta podem ser configurados por variáveis de ambiente:
            - QDRANT_HOST (default: "localhost")
            - QDRANT_PORT (default: 6333)
        """
        host = host or os.getenv("QDRANT_HOST", "localhost")
        port = port or int(os.getenv("QDRANT_PORT", "6333"))

        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = vector_size

        # Verifica se a coleção existe; caso contrário, recria
        try:
            self.client.get_collection(collection_name=self.collection_name)
        except:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )
            print(f"Coleção '{self.collection_name}' criada.")
        
        # Cria índice para o campo de data (Payload Index), para garantir consultas eficientes por data
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="last_updated",
                field_schema=PayloadSchemaType.KEYWORD  # KEYWORD é ideal para o formato ISO string
            )
            print("Índice 'last_updated' criado com sucesso.")
        except Exception:
            # Índice já existe ou falha na criação (ignora se já existe)
            pass 


    def add_documents(self, docs):
        """
        Adiciona documentos no Qdrant.

        docs: lista de dicionários com as seguintes chaves:
            - 'chunk': texto processado
            - 'source': URL ou origem
            - 'last_updated': momento da última atualização do chunk
            - 'embedding': vetor gerado pelo modelo de embeddings
        """
        points = []        
        for doc in docs:
            # Extrai o ID único (point_id) e o vetor de embedding
            point_id = doc.pop("point_id")
            vector = doc.pop("embedding")
            
            # O resto do dicionário 'doc' vira o payload (metadados)
            payload = doc 
            
            # Cria a estrutura PointStruct, essencial para o Qdrant
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name, 
            points=points,
            wait=True # Garante que a operação é concluída antes de prosseguir
        )
        print(f"{len(points)} documentos adicionados à coleção '{self.collection_name}'.")

    def search(self, query_vector, top_k=5):
        """
        Executa uma busca vetorial no Qdrant.
        
        query_vector: embedding de consulta (lista ou array)
        top_k: número de resultados a retornar
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return results
