import os
from dotenv import load_dotenv

load_dotenv()

# --- Chunking ---
MIN_CHUNK_CHARS = 100
TARGET_CHUNK_CHARS = 600
MAX_CHUNK_CHARS = 1500

# --- Embedding ---
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
EMBEDDING_DIMENSIONS = 1024

# --- Retrieval ---
TOP_K = 5
SIMILARITY_THRESHOLD = 0.3
DISTANCE_METRIC = "cosine"

# --- Vector Store ---
VECTOR_STORE = "chromadb"          # "chromadb" | "qdrant" | "pgvector"
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "dietary_guidance"

# --- LLM ---
LLM_PROVIDER = "groq"             # "groq" | "openai" | "ollama"
LLM_MODEL = "openai/gpt-oss-120b"
LLM_TEMPERATURE = 0.1             # Low temperature for factual grounding

# --- Guardrails ---
RELEVANCE_THRESHOLD = 0.6
MAX_TOKENS_RESPONSE = 1024
