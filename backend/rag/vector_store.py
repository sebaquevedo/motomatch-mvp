import lancedb

from config import VECTORS_DIR

TABLE_NAME = "motorcycle_parts"


class VectorStore:
    """Thin wrapper over LanceDB for storing and searching chunk embeddings."""

    def __init__(self, db_path=None):
        db_path = str(db_path or VECTORS_DIR)
        VECTORS_DIR.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(db_path)
        self.table_name = TABLE_NAME

    def reset(self):
        """Drop the table if it exists, so a re-seed starts clean."""
        try:
            self.db.drop_table(self.table_name)
        except Exception:
            # Table does not exist yet — nothing to drop.
            pass

    def add_embeddings(self, doc_id, chunks, embeddings):
        data = [
            {
                "id": f"{doc_id}_{i}",
                "doc_id": doc_id,
                "chunk_index": i,
                "chunk_text": chunk,
                "vector": emb,
            }
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]
        if not data:
            return

        try:
            table = self.db.open_table(self.table_name)
            table.add(data)
        except (FileNotFoundError, ValueError):
            self.db.create_table(self.table_name, data=data)

    def search(self, query_embedding, top_k=5):
        try:
            table = self.db.open_table(self.table_name)
        except (FileNotFoundError, ValueError):
            return []
        return table.search(query_embedding).limit(top_k).to_list()
