# M2Rag Deployment Plan

This document outlines the strategy for deploying the M2Rag project, separating the frontend and backend deployments to leverage the strengths of Vercel and Railway, respectively.

## 1. Objectives

- Deploy the FastAPI backend to Railway.
- Deploy the HTML/JS frontend to Vercel.
- Maintain existing RAG functionality, including ChromaDB retrieval, guardrails, and LLM generation.
- Ensure seamless communication between the Vercel-hosted frontend and the Railway-hosted backend using CORS.

## 2. Architecture

- **Backend (Railway):** FastAPI (`main.py`, `src/api/routes.py`) serving the API endpoints (e.g., `/chat`). Railway is well-suited for Python applications and Docker-based deployments.
- **Frontend (Vercel):** Static HTML/CSS/JS (`src/static/index.html`, `src/static/app.js`, `src/static/style.css`). Vercel provides excellent global CDN delivery for static assets and frontend applications.
- **Vector DB:** Local ChromaDB (`chroma_db/`). In a production setting, this should ideally be hosted on a persistent volume or a managed vector database service, but for this deployment, it will be bundled with the backend image or mounted via a persistent volume on Railway.

## 3. Step-by-Step Deployment Plan

### Phase 1: Backend Deployment on Railway

1. **Prepare for Railway:**
   - Ensure `requirements.txt` is up-to-date with all backend dependencies (`fastapi`, `uvicorn`, `chromadb`, `sentence-transformers`, `groq`, etc.).
   - Ensure the application starts correctly using a `Procfile` or Railway start command, e.g., `uvicorn main:app --host 0.0.0.0 --port $PORT`.

2. **CORS Configuration:**
   - Update `main.py` or `src/api/routes.py` to configure CORS middleware. Initially, allow `*` or localhost for testing, but eventually restrict it to the Vercel deployment URL.

3. **Deploy to Railway:**
   - Connect the GitHub repository to Railway.
   - Provision a new service from the repository.
   - Add necessary Environment Variables in the Railway dashboard (e.g., `GROQ_API_KEY`, etc.).
   - Add a persistent volume in Railway if the `chroma_db` directory needs to persist across redeployments, or ensure the vector DB is built/bundled correctly during the deployment process.

### Phase 2: Frontend Deployment on Vercel

1. **Prepare Frontend Assets:**
   - Extract the contents of `src/static` into a separate directory if needed, or simply configure Vercel to serve from the `src/static` directory.
   - Update `app.js` API call endpoints to point to the live Railway backend URL instead of `http://localhost:8000`.

2. **Deploy to Vercel:**
   - Connect the GitHub repository to Vercel.
   - Set the Root Directory to `src/static` (or wherever the frontend files are located).
   - Leave the build command empty (since it's plain HTML/JS).
   - Deploy the project.

### Phase 3: Integration and Testing

1. **Update CORS on Backend:**
   - Once the Vercel deployment is live, copy the generated Vercel URL.
   - Update the Railway backend's `main.py` CORS origins to explicitly allow the Vercel URL.
   - Trigger a redeployment on Railway to apply the changes.

2. **End-to-End Testing:**
   - Access the Vercel frontend URL.
   - Send chat messages and verify that the request successfully hits the Railway backend and returns a RAG-augmented response.
   - Test edge cases (out of scope questions, complex queries) to ensure the guardrails and the generator work perfectly.

## 4. Potential Risks & Mitigations

- **ChromaDB Persistence on Railway:** By default, Railway's file system is ephemeral. If new documents are added or the database is updated dynamically, the changes will be lost on redeploy.
  - *Mitigation:* Attach a Persistent Volume to the Railway service and configure `chroma_db` to save data to that volume path.
- **Cold Starts:** If the Railway service goes to sleep (depending on the plan), the first query might take a while to spin up the FastAPI app and load the embedding models.
  - *Mitigation:* Use a paid Railway plan or set up a cron job/pinger to keep the service awake.
- **CORS Issues:** Browsers might block requests if CORS is not configured perfectly.
  - *Mitigation:* Carefully configure FastAPI's `CORSMiddleware` and check the browser console for specific CORS errors.

## 5. Timeline

- **Phase 1 (Backend - Railway):** 1-2 hours. Configuring environment, checking paths, and setting up persistent volumes if necessary.
- **Phase 2 (Frontend - Vercel):** 30 minutes. Pointing API URLs and deploying static files.
- **Phase 3 (Integration & Final Polish):** 1 hour. Updating CORS, testing cross-origin requests, and handling edge cases.
