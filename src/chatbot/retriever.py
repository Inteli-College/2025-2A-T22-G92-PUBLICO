import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

# --- Embedder ---
class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print("Inicializando Embedder...")
        self.model = SentenceTransformer(model_name)
        print("Embedder inicializado com sucesso.\n")
    
    def encode(self, text):
        return self.model.encode(text)

# --- VectorDB (Qdrant) ---
class VectorDB:
    def __init__(self, collection_name="documents", host="localhost", port=6333):
        print("Inicializando VectorDB (Qdrant)...")
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self._check_collection()
        print(f"Conectado ao Qdrant na coleção '{collection_name}'.\n")
    
    def _check_collection(self):
        # Verifica se a coleção existe
        if self.collection_name not in [c.name for c in self.client.get_collections().collections]:
            print("Coleção não encontrada. Criando nova coleção...")
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
    
    def search(self, query_vector, top_k=5):
        # Busca pontos mais similares
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
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
                "source": h.payload.get("source", "")
            })
        return results

# --- Função principal do retriever ---
def retrieve(query, top_k=5):
    print("--- Iniciando processo de busca ---")
    print(f"Consulta recebida: '{query}'")

    embedder = Embedder()
    vectordb = VectorDB()

    print("Gerando embedding da query...")
    query_embedding = embedder.encode(query)
    print(f"Embedding gerado (mostrando primeiros 5 valores): {query_embedding[:5]}\n")

    print(f"Buscando top {top_k} resultados no Qdrant...")
    try:
        top_results = vectordb.search(query_embedding, top_k=top_k)
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar no Qdrant: {e}")

    print(f"{len(top_results)} resultados encontrados.\n")
    print("Top resultados:")
    for r in top_results:
        print({
            "id": r["id"],
            "score": r["score"],
            "chunk": r["chunk"],
            "source": r["source"]
        })
    
    return top_results

# --- Execução direta para teste ---
if __name__ == "__main__":
    query = input("Digite sua query: ")
    retrieve(query, top_k=5)