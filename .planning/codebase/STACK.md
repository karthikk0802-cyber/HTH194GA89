---
last_mapped_commit: 39d2d8cb910ac84883ea29f2a4f16d44679d579e
last_mapped_at: 2026-09-25
---
# Technology Stack

**Analysis Date:** 2026-09-25

## Languages

**Primary:**

- Python 3.14 (observed runtime; `server.py`, `services/`, `scripts/`, `tests/`) - Backend API, RAG pipeline, adaptive learning logic
- JavaScript (ES modules, JSX) - React 19 frontend in `src/`

**Secondary:**

- None detected (no TypeScript — frontend is plain `.jsx`/`.js`)

## Runtime

**Environment:**

- Python 3.14.7 (verified via `python3 --version`)
- Node.js v24.21.0 (verified via `node --version`)

**Package Manager:**

- Backend: pip with `requirements.txt`
- Frontend: npm
- Lockfile: `package-lock.json` present (npm); no pip lockfile (`requirements.txt` only, lower-bound pins with `>=`)

## Frameworks

**Core:**

- FastAPI `>=0.110.0` - Backend REST API (`server.py`: `app = FastAPI(title="OnboardIQ API Server", version="2.0.0")`)
- React `^19.2.8` + ReactDOM `^19.2.8` - Frontend UI (`src/App.jsx`, `src/pages/`, `src/components/`)
- SQLAlchemy `>=2.0.28` - ORM for both SQLite databases (`services/db.py`, `services/auth_db.py`)
- Pydantic `>=2.6.4` - Request/response validation (`server.py` imports `BaseModel`; ~15 request models e.g. `RegisterRequest`, `QARequest`, `QuizSubmitRequest`)

**Testing:**

- pytest `>=8.1.1` - Backend unit tests (`tests/test_core_logic.py`, `tests/test_brief_fixes.py`, `tests/test_concept_fixes.py`, `tests/test_kb_golden.py`)

**Build/Dev:**

- Vite `^8.3.0` + `@vitejs/plugin-react ^6.1.1` - Frontend dev server and production build (`vite.config.js`, `package.json` scripts: `dev`, `build`, `preview`)
- Uvicorn `>=0.29.0` - ASGI server launched from `server.py:1398-1399` (`uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)`)
- oxlint `^1.81.0` - Frontend linter (`package.json` script `lint`, config `.oxlintrc.json` with `react` + `oxc` plugins)

## Key Dependencies

**Critical:**

- `mistralai>=0.1.3` - LLM completions via `services/llm.py` (`get_mistral_client()`, `generate_completion()` with multi-model fallback chain: `mistral-small-latest` → `mistral-medium-latest` → `open-mistral-7b` → `mistral-large-latest`)
- `chromadb>=0.4.24` - Persistent vector store for grounded RAG (`services/embedding.py`: `chromadb.PersistentClient(path="./chroma_db")`, collection `nexora_knowledge_base`, cosine HNSW space)
- `sentence-transformers>=2.6.1` - Embedding function (indirect: `chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")` in `services/embedding.py:12`)
- `python-dotenv>=1.0.1` - Env loading (`server.py:10` `load_dotenv()`, `services/llm.py:7`)
- `python-multipart>=0.0.9` - Multipart form parsing for file uploads (`server.py` `UploadFile`/`File`/`Form` endpoints: `/api/admin/docs/upload`, `/api/v2/profile/resume`)

**Infrastructure:**

- `networkx>=3.2.1` - Competency DAG (`services/adaptive.py:1` `import networkx as nx`; `build_competency_graph()`; validated by `scripts/validate_dag.py`)
- `PyMuPDF>=1.24.1` - PDF text extraction (`services/document_processor.py:1` `import pymupdf as fitz`)
- `python-docx>=1.1.0` - DOCX text extraction (`services/document_processor.py:2` `import docx`)
- `plotly>=5.20.0` - Declared in `requirements.txt`; no direct import found in `services/` or `server.py` (likely used by reporting/export scripts or reserved for dashboard charts — treat as declared-but-unverified)
- `hashlib` (stdlib) - Password hashing (`services/auth_db.py:55` SHA-256 with static salt)
- `sqlite3` (stdlib) - Additive schema migrations (`services/db.py:ensure_schema()`, `services/auth_db.py:ensure_auth_schema()`)

## Configuration

**Environment:**

- `.env` file present at repo root (contents never read per policy) + `.env.example` documents the contract:
  - `MISTRAL_API_KEY` - LLM provider key (optional; offline `smart_fallback_completion()` in `services/llm.py` when missing/placeholder)
  - `ADMIN_USERNAME` / `ADMIN_PASSWORD` (defaults `admin` / `admin@123`) - Admin seed credentials
  - `DEFAULT_EMPLOYEE_PASSWORD` (default `employee@123`) - First-login password for admin-created users
  - Optional: `ADMIN_PASSWORD_HASH`, `ADMIN_EMAIL`, `ADMIN_FULL_NAME`, `ADMIN_DEPARTMENT`
  - Frontend flags: `VITE_ENABLE_DEMO_LOGIN`, `VITE_QUIZ_V2`, `VITE_RESUME_PROFILE`
- CORS wide open in `server.py:68-74` (`allow_origins=["*"]`)
- Frontend API base hardcoded: `src/services/api.js:1` (`const API_BASE = 'http://localhost:8000/api'`) — no env-based base URL

**Build:**

- `vite.config.js` - Vite + React plugin, dev port `5173`, no proxy (frontend calls FastAPI directly)
- `index.html` - App entry (`/src/main.jsx`), theme bootstrap, title `OnboardIQ | Nexora`
- `package.json` - Scripts: `dev` (vite), `build` (vite build), `preview`, `lint` (oxlint)
- `requirements.txt` - 14 lower-bound (`>=`) backend deps, no upper pins
- `run.bat` - Windows launcher: `pytest tests/ -v` → `python server.py` (port 8000) → `npm run dev` (port 5173)

## Platform Requirements

**Development:**

- Python 3.14 + `pip install -r requirements.txt`
- Node.js 24 + `npm install`
- Copy `.env.example` to `.env` and set `MISTRAL_API_KEY` (optional — offline fallback works without it)
- Ports `8000` (backend) and `5173` (frontend) must be free
- First boot self-seeds: demo auth users, admin account, KB ingest (`server.py:77-100` `_self_seed_on_boot()`)

**Production:**

- No Dockerfile, container config, or hosting manifest detected — deployment target is undefined
- ASGI app importable as `server:app`; serve with `uvicorn server:app --host 0.0.0.0 --port 8000`
- Frontend is a static Vite build (`dist/` exists at repo root) served separately
- Persistent state lives in local files (`./onboardiq.db`, `./auth.db`, `./chroma_db/`) — must be volume-mounted or migrated to managed storage for any hosted deploy

---

*Stack analysis: 2026-09-25*
