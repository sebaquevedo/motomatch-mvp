from sqlalchemy.orm import Session

from db.models import Document
from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStore


class Retriever:
    def __init__(self, db_session: Session):
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStore()
        self.db_session = db_session

    def retrieve_context(self, query: str, top_k=5):
        """Retrieve relevant chunks for a query, enriched with source titles."""
        query_embedding = self.embeddings.embed_text(query)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        context = []
        for result in results:
            doc_id = result["doc_id"]
            document = (
                self.db_session.query(Document)
                .filter(Document.id == doc_id)
                .first()
            )
            context.append(
                {
                    "chunk_text": result["chunk_text"],
                    "source_doc": document.title if document else "Unknown",
                    "distance": result.get("_distance", None),
                    "doc_id": doc_id,
                }
            )
        return context
