import re
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2", chunk_size=200):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size

    def chunk_text(self, text: str):
        """Divide o texto em pedaços fixos."""
        tokens = text.split()
        for i in range(0, len(tokens), self.chunk_size):
            yield " ".join(tokens[i : i + self.chunk_size])

    def embed(self, texts):
        """Transforma lista de textos em embeddings SBERT."""
        return self.model.encode(texts, convert_to_numpy=True)
