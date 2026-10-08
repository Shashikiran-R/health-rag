import chromadb
import sys
import os

# Set up paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(SCRIPT_DIR, "chroma_db")
COLLECTION_NAME = "dietary_guidance"

print(f"Connecting to ChromaDB at: {CHROMA_PERSIST_DIR}")

# Initialize ChromaDB client
try:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
except Exception as e:
    print(f"Error connecting to ChromaDB: {e}")
    sys.exit(1)

# Get the collection
try:
    collection = client.get_collection(name=COLLECTION_NAME)
    count = collection.count()
    print(f"Found collection '{COLLECTION_NAME}' with {count} items.\n")
except Exception as e:
    print(f"Error getting collection '{COLLECTION_NAME}': {e}")
    sys.exit(1)

if count == 0:
    print("The collection is empty.")
    sys.exit(0)

# Fetch a few items (e.g., 3 items)
print("Fetching 3 samples from the collection...")
results = collection.get(
    limit=3,
    include=["embeddings", "documents", "metadatas"]
)

# Display the results
if not results['ids']:
    print("No data retrieved.")
    sys.exit(0)

for i in range(len(results['ids'])):
    print("-" * 50)
    print(f"Item {i+1}:")
    print(f"ID: {results['ids'][i]}")
    
    # Metadata
    metadata = results['metadatas'][i] if results['metadatas'] else None
    print(f"Metadata: {metadata}")
    
    # Document
    document = results['documents'][i] if results['documents'] else None
    # Truncate document if it's too long for display
    doc_display = document[:200] + "..." if document and len(document) > 200 else document
    print(f"Document snippet: {doc_display}")
    
    # Embeddings
    embedding = results['embeddings'][i] if results['embeddings'] else None
    if embedding:
        # Show first 5 dimensions and the total length
        emb_display = f"{embedding[:5]} ... (Total dimensions: {len(embedding)})"
        print(f"Embedding: {emb_display}")
    else:
        print("Embedding: None")
        
print("-" * 50)
