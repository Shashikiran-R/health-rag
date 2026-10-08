import chromadb
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(SCRIPT_DIR, "chroma_db")

print(f"Connecting to ChromaDB at: {CHROMA_PERSIST_DIR}")

# Initialize ChromaDB client
try:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
except Exception as e:
    print(f"Error connecting to ChromaDB: {e}")
    sys.exit(1)

collections = client.list_collections()
print("Available collections:")
for c in collections:
    print(c.name)
