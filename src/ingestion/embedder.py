import chromadb
from chromadb.utils import embedding_functions
from src.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL, DISTANCE_METRIC
from src.ingestion.chunker import Chunk

def build_index(chunks: list[Chunk]) -> None:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn,
        metadata={"hnsw:space": DISTANCE_METRIC}
    )

    texts = [c.text for c in chunks]
    ids = [c.chunk_id for c in chunks]
    metadatas = [
        {
            "document_id": c.document_id,
            "section_heading": c.section_heading,
            "publisher": str(c.metadata.get("publisher", "")),
            "year": int(c.metadata.get("year", 0)),
            "url": str(c.metadata.get("url", "")),
        }
        for c in chunks
    ]

    collection.upsert(documents=texts, ids=ids, metadatas=metadatas)
