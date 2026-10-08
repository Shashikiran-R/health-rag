import json
import chromadb
from chromadb.utils import embedding_functions
import os
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNKS_FILE = os.path.join(SCRIPT_DIR, "chunks.jsonl")
CHROMA_PERSIST_DIR = os.path.join(SCRIPT_DIR, "chroma_db")
COLLECTION_NAME = "dietary_guidance"

print(f"Connecting to ChromaDB at: {CHROMA_PERSIST_DIR}")

# Initialize ChromaDB client
try:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
except Exception as e:
    print(f"Error connecting to ChromaDB: {e}")
    sys.exit(1)

# Set up embedding function
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5")

# Get or create collection
collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=emb_fn)

print("Reading chunks from chunks.jsonl...")
chunks = []
with open(CHUNKS_FILE, 'r') as f:
    for i, line in enumerate(f):
        if i >= 5:  # Let's just process the first 5 chunks for demonstration
            break
        chunks.append(json.loads(line))

if not chunks:
    print("No chunks found in the file.")
    sys.exit(0)

print(f"Preparing to add {len(chunks)} chunks to ChromaDB...")

ids = []
documents = []
metadatas = []

for chunk in chunks:
    ids.append(chunk['chunk_id'])
    documents.append(chunk['text'])
    metadatas.append(chunk['metadata'])

# Add to collection (will automatically embed using BAAI/bge-large-en-v1.5)
print("Adding and embedding chunks in ChromaDB...")
collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print("\nSuccessfully added chunks. Now retrieving a few embeddings from ChromaDB...")

# Retrieve
results = collection.get(
    limit=3,
    include=["embeddings", "documents", "metadatas"]
)

if not results['ids']:
    print("No data retrieved.")
    sys.exit(0)

for i in range(len(results['ids'])):
    print("-" * 50)
    print(f"Item {i+1}:")
    print(f"Chunk ID: {results['ids'][i]}")
    
    metadata = results['metadatas'][i] if results['metadatas'] else None
    print(f"Metadata: {metadata}")
    
    document = results['documents'][i] if results['documents'] else None
    doc_display = document[:100].replace('\n', ' ') + "..." if document and len(document) > 100 else document
    print(f"Document snippet: {doc_display}")
    
    embedding = results['embeddings'][i] if results.get('embeddings') is not None else None
    if embedding is not None:
        emb_display = f"{[round(e, 4) for e in embedding[:5]]} ... (Total dimensions: {len(embedding)})"
        print(f"Embedding vector (first 5 elements): {emb_display}")
    else:
        print("Embedding vector: None")
        
print("-" * 50)
print(f"\nTotal items now in '{COLLECTION_NAME}' collection: {collection.count()}")
