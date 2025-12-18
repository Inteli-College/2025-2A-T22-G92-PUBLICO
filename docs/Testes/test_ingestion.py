# Responsável por testar a funcionalidade do módulo de ingestão

from qdrant_client import QdrantClient
from qdrant_client.http import models

def test_qdrant_vector_insertion():
    # Conecta ao Qdrant local (Docker deve estar rodando)
    client = QdrantClient(host="127.0.0.1", port=6333)

    # Cria uma coleção de teste
    client.recreate_collection(
        collection_name="test_collection",
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )

    # Vetor de teste
    test_vector = [0.1] * 384

    # Insere o vetor
    client.upsert(
        collection_name="test_collection",
        points=[
            models.PointStruct(id=1, vector=test_vector, payload={"source": "unit_test"})
        ]
    )

    # Busca o vetor pelo ID
    result = client.retrieve(collection_name="test_collection", ids=[1])

    # Valida se o vetor foi salvo corretamente
    assert len(result) == 1, "O vetor deve ser recuperado com sucesso."
    assert result[0].payload["source"] == "unit_test", "O payload deve corresponder ao inserido."
