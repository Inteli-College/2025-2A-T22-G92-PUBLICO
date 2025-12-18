import os
from qdrant_client import QdrantClient
from typing import List, Dict, Any
from qdrant_client.models import (
    VectorParams,
    PointStruct,
    Distance,
    PayloadSchemaType,
    Filter,
    FieldCondition,
    MatchValue,
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

    def search(self, query_vector, top_k=5, query_filter: Filter = None):
        """
        Executa uma busca vetorial no Qdrant, aplicando um filtro de acordo com permissão de acesso.
        
        query_vector: embedding de consulta (lista ou array)
        top_k: número de resultados a retornar
        query_filter: (Opcional) Objeto de Filtro do Qdrant para segurança/metadados.
        """
        # Busca pontos mais similares
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )
        results = []
        for h in hits:
            # Detecta automaticamente o campo de texto do payload
            if "chunk" in h.payload:
                chunk_text = h.payload["chunk"]
            elif "text" in h.payload:
                chunk_text = h.payload["text"]
            else:
                # Pega qualquer campo de string disponível
                chunk_text = next((v for v in h.payload.values() if isinstance(v, str)), "")
            
            results.append({
                "id": h.id,
                "score": h.score,
                "chunk": chunk_text,
                "source": h.payload.get("source", ""),
                "chunk_index": h.payload.get("chunk_index"),
                "last_updated": h.payload.get("last_updated"),
                "file_in_storage": h.payload.get("file_in_storage"), 
                "display_name": h.payload.get("display_name"),
            })
        return results

    def get_chunks_by_metadata(self, source: str, chunk_index: int, user_role: str) -> List[Dict[str, Any]]:
                """
                Busca chunks específicos na coleção usando os campos 'source' e 'chunk_index' no payload,
                aplicando também o filtro de segurança (user_role). Importante para retornar chunks
                vizinhos e dar mais contexto para o chunk escolhido e, assim, para o LLM.
                """
                # Constrói o filtro de metadados (Source, Index, e Segurança)
                metadata_filter = Filter(
                    must=[
                        FieldCondition(key="allowed_roles", match=MatchValue(value=user_role)),
                        FieldCondition(key="source", match=MatchValue(value=source)),
                        FieldCondition(key="chunk_index", match=MatchValue(value=chunk_index)),
                    ]
                )
                
                # Executa a busca. Como o Qdrant exige um vetor de busca (query_vector), deve-se usar um vetor dummy (composto apenas por 1.0) para que a busca seja guiada apenas pelo filtro.
                dummy_vector = [0.0] * self.vector_size 

                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=dummy_vector, 
                    query_filter=metadata_filter,
                    limit=1, # apenas o chunk exato
                    with_payload=True, 
                )
                
                results = []
                for h in hits:
                    if "chunk" in h.payload:
                        chunk_text = h.payload["chunk"]
                    elif "text" in h.payload:
                        chunk_text = h.payload["text"]
                    else:
                        chunk_text = next((v for v in h.payload.values() if isinstance(v, str)), "")
                        
                    results.append({
                        "id": h.id,
                        "score": h.score, 
                        "chunk": chunk_text,
                        "source": h.payload.get("source", ""),
                        "chunk_index": h.payload.get("chunk_index"),
                        "last_updated": h.payload.get("last_updated"),
                        "file_in_storage": h.payload.get("file_in_storage"), 
                        "display_name": h.payload.get("display_name"),
                    })
                    
                return results