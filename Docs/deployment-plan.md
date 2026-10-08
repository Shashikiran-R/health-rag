# M2Rag Deployment Plan (Streamlit)

This document outlines the strategy for transitioning the M2Rag project from a FastAPI-based backend with static HTML/JS frontend to a unified Streamlit application, and deploying it to the Streamlit Community Cloud.

## 1. Objectives

- Consolidate the frontend and backend into a single Streamlit application.
- Maintain existing RAG functionality, including ChromaDB retrieval, guardrails, and LLM generation.
- Deploy the application seamlessly on Streamlit Community Cloud (or another preferred cloud host) for easy access.

## 2. Architecture Changes

**Current Architecture:**
- **Backend:** FastAPI (`main.py`, `src/api/routes.py`) serving a `/chat` endpoint.
- **Frontend:** Static HTML/JS in `src/static/index.html`.
- **Vector DB:** Local ChromaDB (`chroma_db/`).

**Proposed Architecture (Streamlit):**
- **Unified App:** A single `app.py` Streamlit script replacing FastAPI and HTML/JS. Streamlit handles both the UI and the backend logic natively.
- **Backend Logic:** Directly integrate `src.generation.answer_generator`, `src.guardrails.scope_guard`, and `src.retrieval.retriever` within the Streamlit event loop.
- **Vector DB:** Continue using ChromaDB. Since ChromaDB runs in-memory or from local disk, Streamlit Cloud can load the embedded database from the repository directly. (Note: The `chroma_db` folder must be committed to the repo, or embeddings must be generated dynamically on app startup, which isn't recommended due to timeout constraints).

## 3. Step-by-Step Migration Plan

### Step 1: Create the Streamlit App (`app.py`)
1. Create an `app.py` file in the root of the project.
2. Build the chat interface using `st.chat_input` and `st.chat_message`.
3. Store the chat history in `st.session_state` to maintain the conversation context.
4. Hook up the user input to the existing RAG pipeline (`ChatEngine` or direct pipeline execution).

### Step 2: Manage Environment Variables and Dependencies
1. Add `streamlit` to `requirements.txt`.
2. Ensure all other required dependencies (like `chromadb`, `sentence-transformers`, `groq`, `python-dotenv`) are listed in `requirements.txt`.
3. In local testing, use `.env` to manage API keys. In Streamlit Cloud, move these secrets to the Streamlit Cloud **Secrets Management** dashboard.

### Step 3: Handle the ChromaDB Persistence Directory
1. The `.gitignore` must be checked to ensure `chroma_db/` is **not** ignored if we want Streamlit Cloud to load the pre-computed embeddings.
2. *Alternative:* If `chroma_db/` is too large for GitHub, we can store it in cloud storage (like AWS S3) and download it at startup, or dynamically re-ingest the data on the first run (not recommended for production apps).
3. Update `src/config.py` to ensure paths point correctly to the relative `chroma_db` location.

### Step 4: Local Testing
1. Run `pip install streamlit`.
2. Start the app locally with `streamlit run app.py`.
3. Test edge cases (out of scope questions, complex queries) to ensure the guardrails and the generator work perfectly within the Streamlit loop.

### Step 5: Deployment to Streamlit Community Cloud
1. Push the updated codebase (including `app.py`, updated `requirements.txt`, and the `chroma_db/` directory) to a GitHub repository.
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect your GitHub account and select the repository.
4. Set the Main file path to `app.py`.
5. Under "Advanced Settings", add your API Keys (`GROQ_API_KEY`, etc.) as secrets.
6. Click **Deploy!**

## 4. Potential Risks & Mitigations

- **Database Size on GitHub:** If `chroma_db/` exceeds GitHub's file limits (100MB per file), it will cause push errors.
  - *Mitigation:* Ensure `chunks.jsonl` and the vector database files remain small. If they grow, we might need to use `git-lfs` or external storage.
- **Memory Limits on Streamlit Cloud:** Free tier provides limited RAM (~1GB). SentenceTransformers might consume significant memory when loaded.
  - *Mitigation:* If `BAAI/bge-large-en-v1.5` causes Out of Memory (OOM) errors on Streamlit Cloud, downgrade to a smaller model (e.g., `all-MiniLM-L6-v2`) in `src/config.py` and re-ingest the data.

## 5. Timeline

- **Phase 1 (Frontend Replacement):** 1-2 hours. Writing the Streamlit UI and wiring it to the backend functions.
- **Phase 2 (Local Testing & Refinement):** 1 hour. Ensuring chat history, error states, and citations display nicely.
- **Phase 3 (Deployment & Environment config):** 1 hour. Pushing to GitHub, configuring Streamlit Cloud, and testing live.

---
*Ready to proceed with creating `app.py` whenever you are!*
