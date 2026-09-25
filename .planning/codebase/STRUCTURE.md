---
last_mapped_commit: 39d2d8cb910ac84883ea29f2a4f16d44679d579e
last_mapped_at: 2026-09-25
---
# Codebase Structure

**Analysis Date:** 2026-09-25

## Directory Layout

```
HTH194GA89/                  # OnboardIQ — adaptive corporate onboarding (Nexora demo co.)
├── server.py                # FastAPI monolith: all REST routes (~1399 lines)
├── src/                     # React 19 + Vite SPA frontend
│   ├── main.jsx             # React bootstrap (StrictMode render)
│   ├── App.jsx              # Tab router + admin/learner gating + VITE_QUIZ_V2 flag
│   ├── pages/               # One component per tab/route (13 pages)
│   ├── components/          # Sidebar, Navbar, ChangePassword shell pieces
│   ├── context/             # AuthContext (user/token/stats + localStorage)
│   ├── services/            # api.js — single REST client for the whole backend
│   ├── assets/              # Static images (hero.png, react.svg, vite.svg)
│   ├── App.css / index.css  # Global styles (dark theme via data-theme attr)
├── services/                # Backend domain layer (pure rules + persistence)
│   ├── db.py / auth_db.py   # SQLite models + session factories (2 separate DBs)
│   ├── adaptive.py          # Competency DAG, mastery updates, ranking
│   ├── rag.py / llm.py / embedding.py  # Grounded Q&A stack
│   ├── quiz_generator.py / quiz_validator.py / quiz_policy_v2.py / question_bank.py
│   ├── diagnostic.py / baseline_v2.py   # v1 + v2 pre-assessments
│   ├── roles.py / taxonomy.py           # v1 + v2 role/topic taxonomies
│   ├── readiness.py / gamification.py   # Manager verdicts + XP/streaks/badges
│   ├── scenarios.py / teaching.py / voice.py / resources.py
│   ├── document_processor.py            # Extract → chunk → metadata
│   ├── resume_profile.py / eval_seen.py # Resume calibration + held-out dedup
│   └── admin_auth.py                    # Admin seed + token guard
├── scripts/                 # One-shot batch entry points (ingest/seed/export)
├── tests/                   # pytest suites hitting services directly (no HTTP)
├── knowledge_base/          # 36 SOP sources, PDF+TXT pairs (ingestion input)
├── utils/                   # Single-file stub package (placeholder only)
├── public/                  # Vite static assets served verbatim
├── dist/                    # Vite production build output (generated)
├── chroma_db/               # Chroma persistent vector store (generated, committed)
├── demo_work/               # Local demo scratch output (generated)
├── graphify-out/            # Knowledge-graph exports (generated)
├── auth.db / onboardiq.db (+ .bak)     # Live SQLite files (generated, committed)
├── index.html               # Vite HTML shell (mounts /src/main.jsx)
├── vite.config.js           # Vite + React plugin, dev port 5173
├── package.json / package-lock.json    # Frontend deps (react, vite, oxlint)
├── requirements.txt         # Backend deps (fastapi, chromadb, mistral, etc.)
├── run.bat                  # Windows convenience launcher
├── plan.md / README.md      # Human planning notes + project readme
└── .planning/codebase/      # GSD codebase maps (this file + siblings)
```

## Directory Purposes

**`src/`:**

- Purpose: Entire frontend SPA — tab pages, shell chrome, auth state, API client.
- Contains: `.jsx` components, `api.js` client, `.css` styles, `assets/` images.
- Key files: `src/App.jsx` (router), `src/main.jsx` (bootstrap), `src/services/api.js` (all backend calls), `src/context/AuthContext.jsx` (session state).

**`src/pages/`:**

- Purpose: One full-screen view per sidebar tab; each page owns its data fetching via `api`.
- Contains: 13 page components — `Login.jsx`, `AdminLogin.jsx`, `Dashboard.jsx`, `PreAssessment.jsx`, `PreAssessmentV2.jsx`, `LearningPath.jsx`, `QandA.jsx`, `QuizPractice.jsx`, `QuizPracticeV2.jsx`, `AppliedScenarios.jsx`, `VoiceAndResources.jsx`, `ManagerDashboard.jsx`, `AdminCenter.jsx`, plus `UserManagement.jsx`.
- Key files: `src/pages/Dashboard.jsx` (XP/readiness summary), `src/pages/LearningPath.jsx` (roadmap + graph edges), `src/pages/AdminCenter.jsx` (doc upload/approve/toggle).

**`src/components/` + `src/context/`:**

- Purpose: Persistent shell (sidebar/nav) and cross-page session state.
- Contains: `src/components/Sidebar.jsx`, `src/components/Sidebar.css`, `src/components/Navbar.jsx`, `src/components/Navbar.css`, `src/components/ChangePassword.jsx`, `src/context/AuthContext.jsx`.
- Key files: `src/components/Sidebar.jsx` (learner vs admin nav lists), `src/context/AuthContext.jsx` (login/register/logout, `profileStats`, demo default user).

**`services/`:**

- Purpose: Backend domain layer — every rule the API exposes lives here as an importable function.
- Contains: 22 Python modules (persistence, adaptive, RAG, quiz, taxonomy, gamification, admin).
- Key files: `services/db.py`, `services/auth_db.py`, `services/adaptive.py`, `services/rag.py`, `services/embedding.py`, `services/llm.py`, `services/quiz_generator.py`, `services/taxonomy.py`.

**`scripts/`:**

- Purpose: Offline batch jobs — ingestion, seeding, export, validation, fixture generation.
- Contains: `scripts/ingest_kb.py` (canonical ingest), `scripts/seed_demo_data.py`, `scripts/seed_knowledge_base.py`, `scripts/outcome_export.py`, `scripts/validate_dag.py`, `scripts/expand_kb_docs.py`, `scripts/generate_rich_company_pdfs.py`.
- Key files: `scripts/ingest_kb.py:12-66` (`ingest_all()` — also called on server boot).

**`tests/`:**

- Purpose: Service-level regression suites; no HTTP/E2E harness.
- Contains: `tests/test_core_logic.py`, `tests/test_kb_golden.py`, `tests/test_brief_fixes.py`, `tests/test_concept_fixes.py`, `tests/__init__.py`.
- Key files: `tests/test_core_logic.py` (adaptive/readiness/gamification math), `tests/test_kb_golden.py` (grounded-content pins).

**`knowledge_base/`:**

- Purpose: Source-of-truth SOP corpus that ingestion chunks into Chroma + SQLite.
- Contains: 18 topics × (`.pdf` + `.txt`) — e.g., `Security_Policy_v2.1.pdf`, `Git_Workflow_v1.2.txt`, `Employee_Handbook_v1.0.txt`, `Deployment_SOP.txt`, `Sales_Playbook.txt`.
- Key files: Any `*.txt` is what `extract_text` actually parses when both extensions exist PDFs take precedence in `scripts/ingest_kb.py:32-33`.

**`utils/`:**

- Purpose: Placeholder package — contains only `utils/__init__.py` (empty stub). Do not place new code here; use `services/` (backend) or `src/services/` (frontend).

## Key File Locations

**Entry Points:**

- `server.py:1397-1399`: Backend boot (`uvicorn.run("server:app", port=8000, reload=True)`).
- `server.py:61-65`: `app = FastAPI(...)` instance all routes attach to.
- `index.html:16-17`: HTML shell mounting `src/main.jsx`.
- `src/main.jsx:6-10`: React root render.
- `src/App.jsx:138-144`: `App()` wrapping `MainApp` in `AuthProvider`.
- `scripts/ingest_kb.py:67-69`: `if __name__ == "__main__": ingest_all()` CLI entry.

**Configuration:**

- `vite.config.js`: Vite + `@vitejs/plugin-react`, dev port 5173, no proxy (frontend calls backend directly).
- `package.json`: Frontend deps (`react@19`, `vite@8`, `oxlint`); scripts `dev/build/lint/preview`.
- `requirements.txt`: Backend deps (fastapi, uvicorn, sqlalchemy, chromadb, mistralai, networkx, etc.).
- `.oxlintrc.json`: Frontend lint rules (see CONVENTIONS.md).
- `index.html:2`: `data-theme="dark"` default with `localStorage` override (`onboardiq_theme`).
- `.env` / `.env.example`: Backend secrets presence only — never read or quote (see INTEGRATIONS.md for var names).

**Core Logic:**

- `server.py`: All 12 REST groups with section banners (`# 1. Authentication … # 12. Resume-calibrated hybrid quiz`).
- `services/adaptive.py`: `build_competency_graph()`, `update_topic_state()`, `rank_next_topics()`.
- `services/rag.py`: `generate_rag_response()` + `determine_evidence_confidence()`.
- `services/quiz_generator.py`: `generate_quiz_for_topic()`, `generate_quiz_session()`, `build_graded_eval()`, `FALLBACK_QUIZ_BANK`.
- `services/taxonomy.py`: `ROLE_CARDS`, `DEPARTMENTS`, `get_role_card()`, `apply_bypass_policy()`, `doc_topics_for_title()`.
- `services/roles.py`: v1 `ROLES`, `TOPICS`, `get_role_topics()`.
- `src/services/api.js`: `request()` wrapper + `api` object (one method per backend route).

**Testing:**

- `tests/test_core_logic.py`: Adaptive/readiness/gamification unit checks.
- `tests/test_kb_golden.py`: Golden assertions against grounded KB content.
- `tests/test_brief_fixes.py` / `tests/test_concept_fixes.py`: Targeted regression suites for brief/concept fixes.

## Naming Conventions

**Files:**

- Backend: `snake_case.py` modules named after the domain (`quiz_generator.py`, `quiz_policy_v2.py`, `quiz_validator.py`, `document_processor.py`, `resume_profile.py`, `eval_seen.py`, `admin_auth.py`, `baseline_v2.py`); v2 sidecars always suffixed `_v2` and header-commented as append-only.
- Frontend: `PascalCase.jsx` for components/pages (`QuizPracticeV2.jsx`, `PreAssessment.jsx`, `UserManagement.jsx`, `ChangePassword.jsx`), `camelCase.js` for the client (`api.js`), co-located `Component.css` for styles (`Sidebar.css`, `Navbar.css`).
- Knowledge base: `Title_Case_With_Version.ext` pairs (`Security_Policy_v2.1.pdf` + `.txt`, `Git_Workflow_v1.2.pdf` + `.txt`).
- Tests: `test_<scope>.py` (`test_core_logic.py`, `test_kb_golden.py`).
- Scripts: verb-first `snake_case.py` (`ingest_kb.py`, `seed_demo_data.py`, `outcome_export.py`, `validate_dag.py`).

**Directories:**

- Lowercase plural nouns for code collections: `services/`, `scripts/`, `tests/`, `utils/`, `src/pages/`, `src/components/`, `src/context/`, `src/services/`, `src/assets/`, `knowledge_base/`, `public/`.
- Generated/cached dirs keep tool defaults and are never hand-edited: `dist/`, `node_modules/`, `chroma_db/`, `__pycache__/`, `.pytest_cache/`, `graphify-out/`, `demo_work/`.

## Where to Add New Code

**New Feature (backend endpoint + UI):**

- Primary code: route handler in the matching numbered section of `server.py` + rule function in the matching `services/<domain>.py` (create a new module if no domain fits; never put branching math inline in `server.py` beyond session wiring).
- Tests: new `tests/test_<feature>.py` following the direct-service-call style of `tests/test_core_logic.py` (no HTTP layer).
- Frontend: new page in `src/pages/<Name>.jsx`, one nav entry in `src/components/Sidebar.jsx:5-28`, one `case` in `src/App.jsx:65-118`, one client method on `api` in `src/services/api.js`.

**New Component/Module:**

- Implementation: backend → `services/<domain>.py` with module docstring convention (`# ... — ...` header like `services/quiz_policy_v2.py:1-3`); frontend → `src/components/<Name>.jsx` + optional `src/components/<Name>.css`.
- Shared helpers: backend cross-domain helpers go in the most specific existing `services/*.py` (e.g., grading helpers in `services/diagnostic.py`); frontend shared fetch logic extends `request()`/`api` in `src/services/api.js`, shared session logic extends `src/context/AuthContext.jsx`.

**Utilities:**

- Shared helpers: backend `services/` (there is no active `utils/` — `utils/__init__.py` is an empty stub, do not use it). Frontend: `src/services/api.js` for data access, `src/context/AuthContext.jsx` for session helpers.

## Special Directories

**`chroma_db/`:**

- Purpose: Chroma persistent vector store (`nexora_knowledge_base` collection, cosine space).
- Generated: Yes (written by `services/embedding.py` at runtime / `scripts/ingest_kb.py`).
- Committed: Yes (present in repo snapshot; normally git-ignored elsewhere — treat as rebuildable via `scripts/ingest_kb.py`).

**`dist/` + `node_modules/`:**

- Purpose: Vite build output and npm dependencies.
- Generated: Yes (`npm run build` / `npm install`).
- Committed: `dist/` present in snapshot, `node_modules/` present in workspace; neither should be hand-edited.

**`auth.db` / `onboardiq.db` (+ `.bak`):**

- Purpose: Live SQLite data files (identity vs learning state).
- Generated: Yes (created + self-seeded on first boot via `services/auth_db.py:129`, `services/db.py:66`, `server.py:77-100`).
- Committed: Yes in this snapshot — safe to delete locally to get a clean seed; `.bak` files are manual backups.

**`demo_work/` + `graphify-out/`:**

- Purpose: Scratch/demo outputs and knowledge-graph exports.
- Generated: Yes.
- Committed: Present but disposable; do not import from them.

**`public/`:**

- Purpose: Static files copied verbatim to `dist/` by Vite.
- Generated: No (source).
- Committed: Yes.

**`.planning/`:**

- Purpose: GSD planning state, roadmaps, and these codebase maps (`.planning/codebase/`).
- Generated: Partially (agent-written docs).
- Committed: Per orchestrator git policy; never import code from here.

---
*Structure analysis: 2026-09-25*
