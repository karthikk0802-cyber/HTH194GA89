---
last_mapped_commit: 39d2d8cb910ac84883ea29f2a4f16d44679d579e
last_mapped_at: 2026-09-25
---
# External Integrations

**Analysis Date:** 2026-09-25

## APIs & External Services

**LLM Provider:**

- Mistral AI - All generative features (RAG answers, quiz generation, remediation, scenario grading, voice replies)
  - SDK/Client: `mistralai>=0.1.3` via `services/llm.py:get_mistral_client()` (tries v1+ `Mistral`, v2.x layout, then legacy `MistralClient`)
  - Auth: `MISTRAL_API_KEY` env var (placeholder value `your_mistral_api_key_here` = treated as missing)
  - Behavior: optional — `generate_completion()` falls back to deterministic offline engine `smart_fallback_completion()` when key is missing or all model calls fail; fallback covers quiz JSON, 4-pillar scenario scoring, remediation JSON, ELI5, and policy Q&A
  - Call sites: `services/rag.py:94`, `services/quiz_generator.py`, `services/teaching.py`, `services/scenarios.py`, `services/voice.py` (all funnel through `services/llm.py:generate_completion()`)

**Embeddings:**

- HuggingFace model `BAAI/bge-small-en-v1.5` loaded locally via `chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction` in `services/embedding.py:12`
  - SDK/Client: `sentence-transformers>=2.6.1` (transitive via Chroma helper)
  - Auth: none (local inference, no API key)
  - Note: first run downloads model weights — needs network + disk on cold start

**Other external APIs:**

- None detected. No Stripe, Supabase, Firebase, Auth0, AWS SDK, email/SMS, or analytics imports anywhere in `src/` or `services/`. All HTTP from the frontend is `fetch()` to the local FastAPI backend (`src/services/api.js`).

## Data Storage

**Databases:**

- SQLite `onboardiq.db` (SQLAlchemy) — application data
  - Connection: hardcoded `sqlite:///./onboardiq.db` in `services/db.py:6`
  - Client: SQLAlchemy 2.0 ORM (`SessionLocal`, `declarative_base`)
  - Tables: `documents`, `quiz_feedback`, `user_topic_states`, `user_profiles`, `manager_signoffs` (`services/db.py:11-63`)
  - Committed seed copies `onboardiq.db` / `onboardiq.db.bak` exist at repo root
- SQLite `auth.db` (SQLAlchemy) — isolated credential store
  - Connection: hardcoded `sqlite:///./auth.db` in `services/auth_db.py:8`
  - Client: separate SQLAlchemy engine/session (`AuthSessionLocal`)
  - Tables: `auth_users` with `username`, `email`, `password_hash` (SHA-256 + static salt), `is_admin`, `buddy_username` (`services/auth_db.py:13-24`)
  - Committed seed copies `auth.db` / `auth.db.bak` exist at repo root
- ChromaDB persistent vector store — RAG knowledge base
  - Connection: local path `./chroma_db/` (`services/embedding.py:3` `CHROMA_DATA_PATH`), collection `nexora_knowledge_base`
  - Client: `chromadb.PersistentClient` (`services/embedding.py:11`)
  - Committed index directory `chroma_db/` exists at repo root
  - Lifecycle: `add_chunks_to_chroma()`, `search_chroma()` (client-side status filter: `draft`/`inactive` hidden), `set_document_status()`, `delete_document_from_chroma()`, `reset_collection()`

**File Storage:**

- Local filesystem only. Uploaded PDFs/DOCX/TXT are parsed in-memory (`services/document_processor.py:extract_text()`), chunked (`chunk_text()`, 1000 chars / 200 overlap), and embedded into ChromaDB — original binaries are not persisted
- Seed KB source files live in `knowledge_base/` (paired `.pdf` + `.txt` per policy doc, e.g. `Security_Policy.*`, `Git_Workflow_v1.2.*`); ingested via `scripts/ingest_kb.py` / `scripts/seed_knowledge_base.py`

**Caching:**

- None. No Redis, memcached, or HTTP cache headers. `services/embedding.py` holds one module-level `_collection` singleton (lazy Chroma client), but that is a connection cache, not a data cache

## Authentication & Identity

**Auth Provider:**

- Custom (self-built, no third party)
  - Implementation: username/email + SHA-256 salted password hash in `auth.db` (`services/auth_db.py:52-58`); opaque string tokens `token_{username}_{id}` and `admin_token_{username}_{id}` issued at login (`server.py:209`, `server.py:249`, `server.py:1041`) and checked by `is_admin_token()` / `require_admin()` in `services/admin_auth.py`
  - Public self-registration is disabled (`server.py:161-165` returns 403 without admin token); users are created via `/api/admin/users`
  - Password policy: min 8 chars, must differ from old (`server.py:282-287`); first-login `must_change_password` flag when hash matches `DEFAULT_EMPLOYEE_PASSWORD`
  - Seeded demo accounts (password `password123`, admin via `ADMIN_PASSWORD` env): `sarah_engineer`, `alex_pm`, `mike_devops`, `manager` (admin), `admin` (admin) — see `services/auth_db.py:60-127`

## Monitoring & Observability

**Error Tracking:**

- None. No Sentry, Datadog, or similar SDK

**Logs:**

- `print()` to stdout for operational warnings (`[Startup] self-seed skipped`, `ChromaDB toggle/approve/delete warning`, `Mastery expiry warning`, `[LLM Warning] Mistral AI API calls failed`) and `console.error()` on frontend API failures (`src/services/api.js:18`)
- No structured logging, log levels, or log aggregation

## CI/CD & Deployment

**Hosting:**

- None configured. No Dockerfile, compose file, Procfile, or cloud manifest. Local-only: Uvicorn on `0.0.0.0:8000` + Vite dev server on `5173`; static build output in `dist/`

**CI Pipeline:**

- None. No GitHub Actions / GitLab CI / Jenkins config detected. `run.bat` runs `pytest tests/ -v` as a manual pre-launch gate on Windows only

## Environment Configuration

**Required env vars:**

- `MISTRAL_API_KEY` — optional at runtime (offline fallback), required for live LLM quality
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — admin seed (defaults work for local demo)
- `DEFAULT_EMPLOYEE_PASSWORD` — default `employee@123` if unset
- Frontend `VITE_*` flags (`VITE_ENABLE_DEMO_LOGIN`, `VITE_QUIZ_V2`, `VITE_RESUME_PROFILE`) — optional feature toggles

**Secrets location:**

- Local `.env` file at repo root (present; contents never inspected) loaded by `python-dotenv`; documented contract in `.env.example`
- Hardcoded dev-only secrets exist in code/DB seeds (demo passwords, static hash salt `nexora_onboardiq_secure_salt_2026` in `services/auth_db.py:54`) — local demo only, must not ship to production

## Webhooks & Callbacks

**Incoming:**

- None. All `/api/*` routes in `server.py` are synchronous request/response endpoints; no webhook receivers, no signature verification

**Outgoing:**

- None. No outbound webhooks, email, Slack, or PagerDuty calls — references to `security@nexora.com` / `#security-alerts` / `#incidents` appear only inside policy text and LLM fallback strings, not as integrations

---

*Integration audit: 2026-09-25*
