import numpy as np
from sentence_transformers import SentenceTransformer

def test_embedding_generation_consistency():
    # Carrega o modelo SBERT usado no projeto
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Gera embeddings para o mesmo texto duas vezes
    text = "Política interna de segurança da informação do Bank of America."
    emb1 = model.encode(text)
    emb2 = model.encode(text)

    # Testa se o embedding tem a dimensão correta
    assert len(emb1) == 384, "O vetor de embedding deve ter 384 dimensões."

    # Testa se as duas execuções produzem resultados muito semelhantes
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    assert similarity > 0.99, "Embeddings do mesmo texto devem ser praticamente idênticos."
