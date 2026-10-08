import sys
from src.ingestion.loader import load_blocks
from src.ingestion.chunker import chunk_document
from src.ingestion.embedder import build_index

def main():
    blocks_file = "blocks.jsonl"
    print(f"Loading blocks from {blocks_file}...")
    blocks = load_blocks(blocks_file)
    print(f"Loaded {len(blocks)} blocks.")
    
    print("Chunking documents...")
    chunks = chunk_document(blocks)
    print(f"Created {len(chunks)} chunks.")
    
    print("Building index in ChromaDB...")
    build_index(chunks)
    print("Done. Index built successfully.")

if __name__ == "__main__":
    main()
