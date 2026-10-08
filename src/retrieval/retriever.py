import chromadb
from chromadb.utils import embedding_functions
from src.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL

class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        try:
            self.collection = self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.emb_fn
            )
        except Exception:
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.emb_fn
            )

    def search(self, query: str, k: int = 5, document_id: str = None):
        where_clause = {"document_id": document_id} if document_id else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        return results
