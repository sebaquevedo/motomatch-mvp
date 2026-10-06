from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingService:
    """Local embeddings — no API key required.

    First run downloads the model (~90MB); later runs use the cache.
    """

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        print(f"[OK] Embedding model loaded locally: {MODEL_NAME}")

    def embed_text(self, text):
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts):
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [e.tolist() for e in embeddings]
