---
last_mapped_commit: 39d2d8cb910ac84883ea29f2a4f16d44679d579e
last_mapped_at: 2026-09-25
---
<!-- refreshed: 2026-09-25 -->

# Architecture

**Analysis Date:** 2026-09-25

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│              React SPA Frontend (Vite + React 19)            │
├──────────────────┬──────────────────┬───────────────────────┤
│  Pages           │  Components      │  State + API client   │
│  `src/pages/`    │  `src/components/`│ `src/context/AuthContext.jsx` │
│                  │                  │ `src/services/api.js` │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Monolith API Layer                      │
│         `server.py` (~1399 lines, 12 route groups)           │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              Domain Service Layer                            │
│         `services/` (adaptive, rag, quiz, gamification, ...) │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stores: SQLite auth.db │ SQLite onboardiq.db │ ChromaDB     │
│  `services/auth_db.py`  │ `services/db.py`    │ `services/embedding.py` │
│  Files: `knowledge_base/*.pdf|txt` → chunks via `scripts/ingest_kb.py` │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| API monolith | All REST routes, request/response models, DB session wiring, XP/badge orchestration | `server.py` |
| Auth store | Identity, password hashing, admin/buddy fields, seed demo accounts | `services/auth_db.py` |
| Learning store | Documents, topic states, profiles, signoffs, feedback; additive `ensure_schema()` | `services/db.py` |
| Adaptive engine | Competency DAG, mastery/difficulty updates, spaced-repetition ranking | `services/adaptive.py` |
| RAG coach | Chroma retrieval + Mistral generation, confidence scoring, citation trace | `services/rag.py` |
| Vector store | Chroma persistent collection, role/status-filtered search, lifecycle tagging | `services/embedding.py` |
| LLM gateway | Mistral client negotiation + deterministic offline `smart_fallback_completion` | `services/llm.py` |
| Quiz v1 | Grounded quiz generation, static fallback bank, sessions, graded eval | `services/quiz_generator.py` |
| Quiz gate | Anti-hallucination validation of quiz items against evidence quotes | `services/quiz_validator.py` |
| Quiz policy v2 | Read-only personalization sidecar: difficulty pick, forgetting curve, next-topic | `services/quiz_policy_v2.py` |
| Role taxonomy v1 | Generic roles + 8-topic DAG with prerequisite edges | `services/roles.py` |
| Role taxonomy v2 | Per-role cards (depth + baseline_count), bypass policy, doc→topic mapping | `services/taxonomy.py` |
| Baseline v2 | Per-topic calibrated diagnostic question selection and scoring | `services/baseline_v2.py` |
| Diagnostic v1 | Fixed diagnostic bank, evaluation, answer matching | `services/diagnostic.py` |
| Readiness | READY / READY WITH GAPS / NOT YET READY verdict + markdown report | `services/readiness.py` |
| Gamification | XP awards, level derivation (100 XP/level), streaks, badges | `services/gamification.py` |
| Scenarios | Applied scenario bank + 4-pillar LLM/keyword evaluation | `services/scenarios.py` |
| Teaching | Remediation and explain-again generation | `services/teaching.py` |
| Document pipeline | Text extraction, chunking, metadata inference | `services/document_processor.py` |
| Resources / Voice | Curated per-topic resources; keyword voice-tutor replies | `services/resources.py`, `services/voice.py` |
| Resume profiles | Resume text → skill profile mapped onto role cards (never stores raw text) | `services/resume_profile.py` |
| Eval dedup | Seen-question hashes so held-out evals never repeat practice items | `services/eval_seen.py` |
| Admin guard | Admin seed + `admin_token_` check and `require_admin` dependency | `services/admin_auth.py` |
| Frontend shell | Tab router, admin/learner gating, `VITE_QUIZ_V2` feature flag | `src/App.jsx` |
| Frontend API client | Single `request()` wrapper + `api` object covering every backend route | `src/services/api.js` |
| Frontend auth state | User/token localStorage persistence, profile stats, demo default user | `src/context/AuthContext.jsx` |
| Ingestion entry | Clears SQLite docs + resets Chroma, then re-ingests `knowledge_base/` | `scripts/ingest_kb.py` |

## Pattern Overview

**Overall:** Layered monolith backend + decoupled SPA frontend (direct REST, no BFF/proxy).

**Key Characteristics:**

- Single FastAPI process owns all 12 API groups; domain logic lives in pure-function `services/` modules that routes orchestrate.
- Frozen-v1 + append-only-v2 sidecar convention: v1 files are never edited; v2 behavior is added in new modules (`services/taxonomy.py`, `services/baseline_v2.py`, `services/quiz_policy_v2.py`) or lazy imports inside `server.py` handlers.
- Grounded-by-construction content: quiz/RAG/scenario paths prefer Chroma evidence and static banks over free LLM synthesis, with explicit validation gates.
- Dual SQLite + file-vector-store persistence with no ORM migrations — additive `ensure_*_schema()` functions instead.

## Layers

**Presentation (React SPA):**

- Purpose: Learner/manager/admin UI via tab switching, no client-side router.
- Location: `src/`
- Contains: Pages (`src/pages/`), shell components (`src/components/Sidebar.jsx`, `src/components/Navbar.jsx`), auth context (`src/context/AuthContext.jsx`), API client (`src/services/api.js`), styles (`src/App.css`, `src/index.css`).
- Depends on: Backend REST at `http://localhost:8000/api` (hardcoded in `src/services/api.js:1`).
- Used by: Browser entry `index.html` → `src/main.jsx` → `src/App.jsx`.

**API (FastAPI route layer):**

- Purpose: Request validation (Pydantic models), auth guards, DB session lifecycle, response shaping.
- Location: `server.py`
- Contains: 12 route groups (auth, roles/diagnostic, learning path, RAG Q&A, quizzes, scenarios/voice, dashboard, manager, admin docs, admin users, v2 adaptive, resume profiles), Pydantic request models (`server.py:105-156`), `_admin_guard` (`server.py:57-59`), startup self-seed (`server.py:77-100`).
- Depends on: Every `services/*` module, both SQLite session factories.
- Used by: Frontend `api` object; no other server-side callers.

**Domain services:**

- Purpose: Pure business rules callable without HTTP (also reused by `scripts/` and `tests/`).
- Location: `services/`
- Contains: Adaptive/readiness/gamification math, RAG/quiz/scenario/teaching generation, taxonomy/roles data, persistence models excluded (those are `services/db.py`, `services/auth_db.py`).
- Depends on: Sibling services (e.g., `services/rag.py` → `services/embedding.py` + `services/llm.py`; `services/quiz_policy_v2.py` → `services/quiz_generator.py` via lazy import), Chroma/SQLite only through `services/embedding.py` and `services/db.py`.
- Used by: `server.py` route handlers, `scripts/*.py`.

**Persistence / retrieval:**

- Purpose: Durable state and grounded evidence.
- Location: `services/auth_db.py`, `services/db.py`, `services/embedding.py`, `./auth.db`, `./onboardiq.db`, `./chroma_db/`, `knowledge_base/`
- Contains: SQLAlchemy models (`UserAuthModel`, `DocumentModel`, `UserTopicState`, `UserProfileModel`, `SignoffModel`, `QuizFeedbackModel`), Chroma collection `nexora_knowledge_base`, 36 source PDFs/TXTs (each in PDF+TXT pairs).
- Depends on: SQLAlchemy, ChromaDB + `BAAI/bge-small-en-v1.5` embedding function.
- Used by: Service layer and route handlers via `AuthSessionLocal` / `SessionLocal` / `get_collection()`.

**Scripts / batch:**

- Purpose: One-shot data operations (ingest, seed, export, validate, PDF generation).
- Location: `scripts/`
- Contains: `scripts/ingest_kb.py`, `scripts/seed_knowledge_base.py`, `scripts/seed_demo_data.py`, `scripts/outcome_export.py`, `scripts/validate_dag.py`, `scripts/expand_kb_docs.py`, `scripts/generate_rich_company_pdfs.py`.
- Depends on: `services/db.py`, `services/document_processor.py`, `services/embedding.py`.
- Used by: Operators and `server.py` startup self-seed (`server.py:95-96` calls `scripts.ingest_kb.ingest_all`).

## Data Flow

### Primary Request Path — Quiz answer submit

1. Learner answers in `src/pages/QuizPractice.jsx` (or `src/pages/QuizPracticeV2.jsx`) → `api.submitQuiz()` in `src/services/api.js:67-71`.
2. `POST /api/quiz/submit` in `server.py:581-617`: fuzzy-matches answer via `is_answer_match` (`services/diagnostic.py`), loads/creates `UserTopicState`, calls `update_topic_state(state, is_correct)` (`services/adaptive.py:17-60`).
3. Awards XP via `award_xp(profile, "quiz_correct")` and recomputes badges via `update_badges()` (`services/gamification.py`), commits both sessions, returns `{is_correct, mastery_score, difficulty, status, xp_gained, new_badges}`.

### RAG Knowledge Coach Q&A

1. `src/pages/QandA.jsx` → `api.askQA(query, role)` (`src/services/api.js:57-58`) → `POST /api/qa/ask` (`server.py:524-527`).
2. `generate_rag_response()` (`services/rag.py:25-99`): `search_chroma(query, n_results=4, role_filter)` (`services/embedding.py:29-69`) filters out `draft`/`inactive` chunks client-side, builds confidence via `determine_evidence_confidence()` distance thresholds.
3. Prompt + context → `generate_completion()` (`services/llm.py:36-79`) with Mistral model fallback chain, else `smart_fallback_completion()`; returns `{timestamp, query, confidence, chunks, answer, citations}` trace verbatim to the frontend.

### Diagnostic → Learning path unlock

1. `src/pages/PreAssessment.jsx` → `api.submitDiagnostic()` (`src/services/api.js:43-47`) → `POST /api/diagnostic/evaluate` (`server.py:354-426`).
2. `evaluate_diagnostic()` (`services/diagnostic.py`) → `apply_bypass_policy()` strips non-bypassable `security` (`services/taxonomy.py:176-178`) → per-topic `UserTopicState` rows created/updated, first-completion-only XP via `award_xp(profile, "preassessment_completed")`.
3. `GET /api/learning-path/{userId}` (`server.py:470-519`): builds `rank_next_topics()` order (`services/adaptive.py:62-94`) over the NetworkX DAG from `build_competency_graph()` (`services/adaptive.py:8-15`), returns `{ranked_topics, today_focus, competencies, graph_edges}` rendered by `src/pages/LearningPath.jsx`.

### Admin doc lifecycle (draft → active → mastery expiry)

1. `src/pages/AdminCenter.jsx` → `api.uploadDocument()` multipart POST (`src/services/api.js:122-132`) → `POST /api/admin/docs/upload` (`server.py:892-931`): `extract_text` + `chunk_text` (`services/document_processor.py`), row created with `status="draft"`, chunks indexed via `add_chunks_to_chroma()` with `status: draft` metadata (invisible to `search_chroma`).
2. `POST /api/admin/docs/approve/{docId}` (`server.py:933-972`, admin-guarded): flips status to `active` in both SQLite and Chroma (`set_document_status`), sets `review_after` +90 days, then demotes affected `Completed` states to `Needs-Review` via `doc_topics_for_title()` (`services/taxonomy.py:198-216`).

**State Management:**

- Backend: per-request SQLAlchemy sessions (`AuthSessionLocal`, `SessionLocal`); no unit-of-work sharing across requests. Per-user learning state is rows (`UserTopicState`, `UserProfileModel`), not server memory.
- Frontend: `AuthContext` (`src/context/AuthContext.jsx`) holds `user`, `token`, `profileStats` with `localStorage` persistence (`onboardiq_user`, `onboardiq_token`); page-level `useState` for `activeTab`, `selectedRole`, `selectedQuizTopic` in `src/App.jsx:29-32`. No Redux/Zustand/router.

## Key Abstractions

**UserTopicState (spaced-repetition cell):**

- Purpose: Single (user, topic) mastery record driving everything adaptive.
- Examples: `services/db.py:32-42`, updated in `services/adaptive.py:17-60`, read in `services/readiness.py:11-43`, `services/quiz_policy_v2.py:25-43`.
- Pattern: `status` in `Locked|Current|Recommended|Needs-Review|Completed`, `difficulty` in `Beginner|Intermediate|Expert`, `mastery_score` 0–100, `review_interval_days` ladder `[1,3,7,14,30]`.

**Competency DAG:**

- Purpose: Prerequisite graph that gates unlock order and ranking.
- Examples: `services/roles.py:14-23` (v1 edges), `services/adaptive.py:8-15` builder, `server.py:508-509` edge serialization.
- Pattern: Rebuilt in-memory with NetworkX on every ranking call; never persisted.

**RAG trace:**

- Purpose: Explainable answer envelope (confidence + chunks + citations).
- Examples: `services/rag.py:45-52`, rendered in `src/pages/QandA.jsx`.
- Pattern: Always returned even on empty query or LLM failure.

**Grounded quiz item:**

- Purpose: MCQ shape that must cite evidence; never freely synthesized.
- Examples: `services/quiz_generator.py:10-100` (`FALLBACK_QUIZ_BANK`), `services/quiz_validator.py`, session builder `generate_quiz_session` (20-question no-repeat).
- Pattern: `{question, options, correct_answer, learning_objective, evidence_quote, validation_passed}`; `/api/quiz/generate` (`server.py:532-546`) falls back to `grounded_fallback_question()` or 503.

**v2 sidecar personalization:**

- Purpose: Adaptive targeting layered over frozen v1 without changing v1 semantics.
- Examples: `services/quiz_policy_v2.py`, `services/baseline_v2.py`, `services/taxonomy.py` header comment (`services/taxonomy.py:1-3`), `GET /api/v2/quiz/next` (`server.py:1205-1233`).
- Pattern: Read-only mirrors of v1 thresholds + additive `{reason}` strings surfaced in the UI.

## Entry Points

**FastAPI application:**

- Location: `server.py:61-65` (`app = FastAPI(...)`), run via `server.py:1397-1399` (`uvicorn.run("server:app", port=8000, reload=True)`).
- Triggers: `uvicorn server:app` / `python server.py`; Vite frontend calls it directly.
- Responsibilities: Route registration, CORS, startup self-seed, all request handling.

**React SPA bootstrap:**

- Location: `index.html:16-17` (`<div id="root">` + `/src/main.jsx`), `src/main.jsx:6-10` (StrictMode render of `src/App.jsx`).
- Triggers: Browser load of Vite dev server (`vite.config.js:8-10`, port 5173) or `dist/` build output.
- Responsibilities: Mount `AuthProvider` → `MainApp` tab router; `VITE_QUIZ_V2` flag in `src/App.jsx:24` selects v1 vs v2 assessment/quiz pages.

**Knowledge ingestion:**

- Location: `scripts/ingest_kb.py:12-66` (`ingest_all()`), auto-invoked on boot when docs table is empty (`server.py:92-96`).
- Triggers: `python scripts/ingest_kb.py`, `python scripts/seed_demo_data.py`, server startup.
- Responsibilities: Parse `knowledge_base/`, chunk, write SQLite `documents` + Chroma vectors.

**Test harness:**

- Location: `tests/` (`tests/test_core_logic.py`, `tests/test_kb_golden.py`, `tests/test_brief_fixes.py`, `tests/test_concept_fixes.py`).
- Triggers: `pytest`.
- Responsibilities: Exercise services directly (no HTTP layer); golden KB assertions pin grounded content.

## Architectural Constraints

- **Threading:** Synchronous FastAPI handlers on a single uvicorn process with `reload=True` (`server.py:1399`); SQLite engines use `check_same_thread=False` (`services/db.py:7`, `services/auth_db.py:9`). No background workers, queues, or async DB access — Chroma/LLM calls block the request thread.
- **Global state:** Module-level Chroma singleton `_collection` in `services/embedding.py:4-18` (lazy, never invalidated except `reset_collection`); demo-user defaults baked into models (`services/db.py:35,47`); `SPACED_INTERVALS` constant (`services/adaptive.py:6`). Frontend demo session defaults in `src/context/AuthContext.jsx:7-20`.
- **Circular imports:** None static; v2 modules deliberately use function-level lazy imports to avoid cycles (e.g., `services/quiz_policy_v2.py:61` imports `generate_quiz_for_topic` inside the function; `server.py` imports `services.resume_profile`, `services.eval_seen`, `services.embedding.set_document_status` inside handlers at `server.py:867,1189,1313`).
- **Schema evolution:** No Alembic/migrations. `Base.metadata.create_all()` plus additive `ensure_schema()` (`services/db.py:69-90`) and `ensure_auth_schema()` (`services/auth_db.py:29-43`) — columns may only be added, never renamed/dropped.
- **Versioning:** No API versioning scheme except the `/api/v2/*` sidecar prefix coexisting with frozen v1 routes; breaking v1 shapes is prohibited by convention comments.

## Anti-Patterns

### Fat route handlers in `server.py`

**What happens:** Business orchestration (state transitions, XP math, badge updates, mastery expiry loops) lives inline in route functions, e.g., diagnostic evaluation (`server.py:354-426`), scenario evaluation (`server.py:654-685`), doc approval with mastery invalidation (`server.py:933-972`).
**Why it's wrong:** Duplicates session open/commit/close blocks in every handler and makes the rules untestable without HTTP; fixes must be repeated per route.
**Do this instead:** Keep pushing pure functions into `services/` (the `services/adaptive.py`, `services/gamification.py`, `services/readiness.py` pattern) and leave `server.py` to validation + session lifecycle + response shaping.

### Hardcoded backend origin in the frontend

**What happens:** `const API_BASE = 'http://localhost:8000/api'` in `src/services/api.js:1`, with multipart uploads duplicating the literal again (`src/services/api.js:126,178`).
**Why it's wrong:** Every environment (preview, Docker, deployed) needs a code edit; no `import.meta.env` indirection unlike the existing `VITE_QUIZ_V2` flag in `src/App.jsx:24`.
**Do this instead:** Read the base URL from a Vite env var with the localhost value as fallback, matching the `VITE_QUIZ_V2` precedent.

### Hand-rolled opaque tokens

**What happens:** Login returns `f"token_{username}_{id}"` (`server.py:209,249`) and admin login returns `f"admin_token_{username}_{id}"` (`server.py:1041`); the frontend gates admin UI with `(token || '').startsWith('admin_token_')` (`src/App.jsx:28`).
**Why it's wrong:** Tokens are forgeable display strings, not signed credentials; any client can claim admin by prefix. The real check (`services/admin_auth.py:require_admin` via `_admin_guard`) only protects some admin routes.
**Do this instead:** Issue signed JWTs (or server-side sessions) and validate them on every protected route, keeping the `admin_token_` prefix only as a UI hint.

## Error Handling

**Strategy:** HTTP layer raises `HTTPException` with status/detail; service layer degrades to grounded fallbacks instead of raising; frontend `request()` throws `Error(detail)` after logging.

**Patterns:**

- Guard-then-raise in routes: 403 for non-admin (`server.py:164,258,1297`), 401 for bad credentials (`server.py:222,1037`), 404 for missing doc/scenario/user (`server.py:860,880,944,1094,1124`), 503 when a topic has no grounded quiz (`server.py:541`), 400/422 for resume parse failures (`server.py:1372,1375`).
- Never-synthesize fallback: quiz generation serves `grounded_fallback_question()` before 503 (`server.py:538-541`); LLM outage serves `smart_fallback_completion()` (`services/llm.py:78-79`); scenario/voice/teaching modules return keyword-scored results without network.
- Best-effort boot and side effects: startup self-seed swallows all exceptions (`server.py:99-100`); Chroma toggle/approve warnings only print (`server.py:869-870,950-951`); `log_seen` failures pass silently (`server.py:573-574,1268-1269`).

## Cross-Cutting Concerns

**Logging:** `print()` to stdout only (`[Startup]`, `[LLM Warning]`, `ChromaDB ... warning`, `Mastery expiry warning`); `console.error`/`console.warn` in `src/services/api.js:19` and `src/context/AuthContext.jsx:37`. No structured logging, levels, or aggregation.
**Validation:** Pydantic `BaseModel` request schemas in `server.py:105-156,995-1015,1148-1150,1273-1282` (including password length/difference rules at `server.py:283-287`); quiz items re-validated through `validate_quiz_question()` (`services/quiz_validator.py`) on both single and session paths (`server.py:545,572`).
**Authentication:** SHA-256(salt+password) in `services/auth_db.py:52-58`; admin token check in `services/admin_auth.py` enforced via `_admin_guard` dependency on mutating admin routes (`server.py:934,1047,1055,1089,1116,1138,1153,1359-1395`); read-only admin listings use inline `is_admin_token` checks; most learner/manager routes trust a `userId` query/body param with no token verification.

---
*Architecture analysis: 2026-09-25*
