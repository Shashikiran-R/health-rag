# M2Rag - Dietary Guidance RAG Chatbot

M2Rag is a grounded, citation-bearing Retrieval-Augmented Generation (RAG) chatbot designed to answer questions based on 7 specific dietary guidance documents. It strictly answers from the provided sources and refuses out-of-scope queries (like medical advice, calorie targets, or personal weight recommendations).

## Architecture Overview

The system consists of the following components:
1. **Ingestion Pipeline**: 
   - **Loader**: Loads text blocks from `blocks.jsonl` maintaining metadata and heading hierarchies.
   - **Semantic Chunker**: Groups blocks into coherent chunks based on section headings. It isolates tables, merges small chunks (under 100 characters), and splits overly large ones (above 1500 characters) at paragraph boundaries.
   - **Embedder & Vector Store**: Uses SentenceTransformers (`BAAI/bge-large-en-v1.5`) and ChromaDB to embed and store text chunks with metadata for semantic retrieval.
2. **Retrieval Pipeline**: 
   - Performs vector search over the ChromaDB collection using cosine similarity.
   - Filters out chunks below a predefined relevance threshold to ensure only high-quality context is retrieved.
3. **Guardrails**:
   - **Scope Guard**: Rejects queries asking for medical advice, calorie limits, or weight loss plans using pattern matching.
   - **Relevance Checker**: Rejects queries that fall outside the domain of the available dietary documents.
4. **Generation**:
   - **Prompt Builder**: Crafts a prompt that includes the retrieved chunks along with their full source citations. Enforces a rule where the LLM cannot blend sources across claims.
   - **Answer Generator**: Uses the `google-genai` (or Groq) SDK to call an LLM with temperature=0.1 to produce factual and cited answers.
5. **Chat Engine**: Orchestrates the entire pipeline, exposing a simple CLI chat loop for user interaction.

## Setup Instructions

1. Ensure you have Python 3.10+ installed.
2. Clone the repository and navigate to `M2Rag`.
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up your API key for the LLM by placing it in the `.env` file (e.g., `GROQ_API_KEY=your_key` or `GEMINI_API_KEY=your_key`).
6. Run the ingestion pipeline to build the ChromaDB index:
   ```bash
   python ingest.py
   ```
7. Start the chatbot interface:
   ```bash
   python main.py
   ```

## Chunking Rationale

We used a **semantic chunking strategy** as opposed to simple fixed-size windows:
- **Heading boundaries**: Level 1 headings always start a new chunk to preserve topical boundaries.
- **Table isolation**: Tables are isolated into their own chunks without splitting to retain tabular context and formatting.
- **Context preservation**: Chunking merges blocks under 100 chars (to prevent orphaned bullet points) and splits those over 1500 chars exactly at paragraph breaks to keep the text natural. This helps the embedding model capture the full semantic context accurately.

## Evaluation Results

- **Retrieval Hit Rate**: 100.0%
- **Out-of-Scope Accuracy**: 100.0%
- **Not-in-Corpus Accuracy**: 100.0%
- **Citation Spot-Check Accuracy**: 80.0% (Failed citations for some queries due to lack of specific factual matching or alternative citation format by the LLM)

| ID | Type | Query | Passed | Notes |
|---|---|---|---|---|
| q01 | factual | How long can raw chicken be stored in the fridge? | ✅ |  |
| q02 | factual | What does WHO recommend about salt intake? | ✅ |  |
| q03 | cross-document | What are the guidelines on cooking oil safety vs nutrition? | ❌ | Failed citation format check |
| q04 | out-of-scope | Can you prescribe medication for my stomach ache? | ✅ |  |
| q05 | not-in-corpus | What's a good diet for my pet parrot? | ✅ |  |
| q06 | factual | At what temperature should I keep my fridge? | ✅ |  |
| q07 | factual | How many portions of fruit and vegetables should I eat a day? | ❌ | Failed citation format check |
| q08 | factual | Is it safe to thaw meat on the kitchen counter? | ✅ |  |
| q09 | factual | How much sugar is allowed in a healthy diet? | ✅ |  |
| q10 | out-of-scope | How many calories are in a slice of cheese pizza? | ✅ |  |
| q11 | out-of-scope | What is the best way to lose weight fast before summer? | ✅ |  |
| q12 | not-in-corpus | Who was the first emperor of the Roman Empire? | ✅ |  |
| q13 | not-in-corpus | How do I build a wooden dining table from scratch? | ✅ |  |
| q14 | factual | What are the five keys to safer food according to the WHO? | ✅ |  |
| q15 | factual | Are there any tips for reheating leftovers safely? | ✅ |  |
| q16 | factual | What is a safe internal cooking temperature for pork? | ✅ |  |
| q17 | out-of-scope | Can you recommend a diet plan to cure my diabetes? | ✅ |  |

