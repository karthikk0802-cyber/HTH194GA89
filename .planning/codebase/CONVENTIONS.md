---
last_mapped_commit: 39d2d8cb910ac84883ea29f2a4f16d44679d579e
last_mapped_at: 2026-09-25
---
# Coding Conventions

**Analysis Date:** 2026-09-25

## Naming Patterns

**Files:**

- Python services: `snake_case.py` — e.g. `services/quiz_generator.py`, `services/quiz_policy_v2.py`, `services/document_processor.py`
- Python tests: `test_<area>.py` — e.g. `tests/test_core_logic.py`, `tests/test_kb_golden.py`, `tests/test_brief_fixes.py`, `tests/test_concept_fixes.py`
- React components/pages: `PascalCase.jsx` — e.g. `src/pages/QuizPracticeV2.jsx`, `src/pages/UserManagement.jsx`, `src/components/Navbar.jsx`, `src/components/ChangePassword.jsx`
- React service/context/css: `camelCase.js` / `PascalCase.jsx` + co-located css — e.g. `src/services/api.js`, `src/context/AuthContext.jsx`, `src/components/Navbar.css`, `src/components/Sidebar.css`
- Versioned sidecars use `V2` suffix, never rename v1: `services/baseline_v2.py`, `services/quiz_policy_v2.py`, `src/pages/PreAssessmentV2.jsx`, `src/pages/QuizPracticeV2.jsx`

**Functions:**

- Python: `snake_case` verbs — `build_competency_graph()`, `update_topic_state()`, `rank_next_topics()` (`services/adaptive.py`), `generate_rag_response()`, `determine_evidence_confidence()` (`services/rag.py`), `chunk_text()`, `extract_text()`, `extract_metadata_from_text()` (`services/document_processor.py`)
- JS: `camelCase` verbs — `request()`, `getDashboardSummary()`, `startQuizSession()` (`src/services/api.js`), `fetchProfileStats()`, `quickSwitchUser()`, `updateXpPoints()` (`src/context/AuthContext.jsx`), `getInitials()` (`src/components/Navbar.jsx`)
- Test functions: `test_<behavior>` — `test_chunking_logic`, `test_adaptive_difficulty_progression`, `test_kb_golden_answers` (`tests/test_core_logic.py`, `tests/test_kb_golden.py`)

**Variables:**

- Python: `snake_case` — `mastery_score`, `review_interval_days`, `next_review_at`, `xp_gained`, `new_badges` (`services/adaptive.py`, `services/gamification.py`); module constants `UPPER_SNAKE` — `SPACED_INTERVALS` (`services/adaptive.py`), `DIAGNOSTIC_QUESTIONS`, `SCENARIOS`, `CURATED_RESOURCES`
- JS: `camelCase` — `activeTab`, `selectedRole`, `selectedQuizTopic`, `adminView`, `todayPlan`, `buddyWatch` (`src/App.jsx`, `src/pages/Dashboard.jsx`); env flags `UPPER_SNAKE` — `QUIZ_V2 = import.meta.env.VITE_QUIZ_V2 === 'true'` (`src/App.jsx`)
- SQLAlchemy models: `PascalCase` + `Model` suffix — `DocumentModel`, `QuizFeedbackModel`, `UserTopicState`, `UserProfileModel`, `SignoffModel` (`services/db.py`); FastAPI schemas: `PascalCase` + `Request` suffix — `RegisterRequest`, `LoginRequest`, `DiagnosticSubmitRequest` (`server.py`)

**Types:**

- Python: no annotations in core services (untyped `def update_topic_state(state, is_correct)` in `services/adaptive.py`); selective annotations at boundaries — `def generate_rag_response(query: str, role: str = "all") -> dict` (`services/rag.py:25`)
- FastAPI/Pydantic: `Optional[str]`, `Dict[str, str]`, `List` with defaults — `role: Optional[str] = "Software Engineer"` (`server.py:105-121`)
- JS: no TypeScript; JSDoc absent; prop shapes are implicit (e.g. `function Dashboard({ selectedRole, setActiveTab })` in `src/pages/Dashboard.jsx`)

## Code Style

**Formatting:**

- Python: no `black`/`ruff`/`flake8` config present (no `pyproject.toml`, `setup.cfg`, `.flake8`); 4-space indent, ~100-col lines, double quotes dominant. Follow the existing file's style; do not reformat whole files.
- JS: no `.prettierrc` / `eslint.config.*`; 2-space indent, single quotes dominant, semicolons required, trailing commas in multiline literals. Follow `src/services/api.js` and `src/App.jsx` style.
- CSS: co-located per component (`src/components/Navbar.css` next to `src/components/Navbar.jsx`); global tokens in `src/index.css` / `src/App.css`.

**Linting:**

- JS only: `oxlint` via `npm run lint` (`package.json:9`), plugins `react` + `oxc`, rules `react/rules-of-hooks: error` and `react/only-export-components: warn` (`./.oxlintrc.json`). No Python linter configured.
- Run `npx oxlint` before frontend changes; keep React hooks unconditional and components as default exports.

## Import Organization

**Order:**

1. Standard library (`os`, `json`, `datetime`, `re`, `io` in `server.py`, `services/document_processor.py`)
2. Third-party (`fastapi`, `pydantic`, `sqlalchemy`, `networkx`, `react` in `server.py`, `services/adaptive.py`, `src/App.jsx`)
3. Local services (`from services.rag import generate_rag_response`, `from services.db import ...` in `server.py`; `import { api } from '../services/api'`, `import { useAuth } from '../context/AuthContext'` in pages)
4. Relative UI imports: pages → components → context → css (see `src/App.jsx:1-22`, `src/components/Navbar.jsx:1-4`)

**Path Aliases:**

- None. Use relative imports only: `../services/api`, `../context/AuthContext`, `./Navbar.css`. Backend uses absolute-from-root `from services.<module> import ...` (never relative `from .rag import ...`).

## Error Handling

**Patterns:**

- Backend endpoints: raise `fastapi.HTTPException` with explicit status codes — `400` validation, `401` auth, `403` admin/registration gating, `404` missing entity, `422` unparseable resume, `503` quiz generation failure (`server.py:165-1394`). Always pass `detail="human-readable message"`.
- Service internals: broad `try/except Exception` with graceful fallback return, never re-raise — return degraded value plus `print("[...] ...")` tag:
  ```python
  # services/rag.py:93-96
  try:
      answer = generate_completion(prompt, temperature=0.3)
  except Exception as e:
      answer = f"I encountered an issue generating the answer: {str(e)}"
  ```
  ```python
  # services/quiz_generator.py:397-398
  except Exception as e:
      print(f"[QuizSession] LLM top-up failed: {e}. Using static bank only.")
  ```
- Startup seeding is best-effort: wrap in `try/except` + `print(f"[Startup] self-seed skipped: {e}")` so boot never fails (`server.py:84-100`).
- Use `services/admin_auth.py:41-69` pattern for auth guards: `require_admin(authorization)` raises `_HTTPException(403)`; endpoint wrapper `_admin_guard()` injects the header via `Depends` (`server.py:57-59`).
- Frontend API layer: single `request()` wrapper in `src/services/api.js:3-21` — parse `err.detail || 'API request failed'`, `console.error('API Error on ${endpoint}:', error)`, re-throw for callers.
- Frontend pages: `try/catch` setting local error state, or promise `.catch(console.error)` / `.catch(() => null)` / `.catch(() => [])` for optional data (`src/pages/Dashboard.jsx:16-29`). Non-critical stats use `console.warn`, e.g. `console.warn('Could not fetch user profile stats:', err)` (`src/context/AuthContext.jsx:37`) and `console.warn('Session answer submit failed:', err)` (`src/pages/QuizPractice.jsx:89`).
- Browser-only APIs (speech synthesis, mic, localStorage) must be guarded: `try { window.speechSynthesis?.cancel(); } catch (e) { /* noop */ }` (`src/pages/VoiceAndResources.jsx:20`).

## Logging

**Framework:** `print()` with bracket tags (backend), `console.error` / `console.warn` (frontend). No `logging` module, no log aggregator.

**Patterns:**

- Backend: `print(f"[QuizGen Warning] LLM generation failed: {e}. Using randomized verified fallback.")` (`services/quiz_generator.py:517`), `print(f"[ScenarioEval Error] {e}")` (`services/scenarios.py:120`), `print(f"[LLM Warning] Mistral AI API calls failed ({last_error}). ...")` (`services/llm.py:78`). Match the existing `[Tag]` prefix convention when adding new warnings.
- Frontend: `console.error` for failed primary fetches (`.catch(console.error)` in `src/pages/Dashboard.jsx:28`, `src/pages/LearningPath.jsx:15`); `console.warn` for optional/degraded paths (profile stats, quiz submit). Never `console.log` in committed code.
- Do not add persistent/file logging; keep diagnostics to stdout/console.

## Comments

**When to Comment:**

- One-line docstrings on every public service function describing the deterministic behavior: `"""Deterministically update mastery score, difficulty, and spaced review schedules."""` (`services/adaptive.py:18`), `"""Calculate confidence based on ChromaDB distance scores ..."""` (`services/rag.py:6`).
- Inline comments mark numbered pipeline stages (`# 1. Retrieve relevant knowledge base chunks`, `# 2. Augment & Generate Prompt` in `services/rag.py:41-76`) and magic thresholds (`# Leveled up past 100 XP` is inline in tests; `# Every 100 XP is a level` in `services/gamification.py:20`).
- Architecture notes as file-top or route comments: `// React frontend talks to the FastAPI backend directly ... No Streamlit server exists anymore` (`vite.config.js:4-5`), `// Role is admin-assigned: view always follows the logged-in user's record.` (`src/App.jsx:44`), `// Admins get the admin portal only — no learner content.` (`src/App.jsx:49`).

**JSDoc/TSDoc:**

- Not used. Document JS functions with plain behavior only when non-obvious; prefer clear names (`grounded_fallback_question`, `effective_mastery`) over annotation comments.

## Function Design

**Size:** Small single-purpose functions (10–40 lines). `update_topic_state()` (`services/adaptive.py:17-60`), `generate_rag_response()` (`services/rag.py:25-99`), `award_xp()` (`services/gamification.py:4-25`). Break out helpers rather than growing endpoint handlers in `server.py`.

**Parameters:** Plain positional args with safe defaults — `chunk_text(text, chunk_size=1000, overlap=200)`, `extract_metadata_from_text(text, default_role="all")`, `generate_rag_response(query, role="all")`, `api.generateQuiz(topic, role='all', difficulty='Beginner')`. Pass SQLAlchemy/duck-typed state objects (`profile`, `state`) and mutate in place, then return them (`services/adaptive.py`, `services/gamification.py`).

**Return Values:** Dict traces with fixed keys — RAG returns `{timestamp, query, confidence, chunks, answer, citations}` (`services/rag.py:45-52`); ranking returns `[{topic_id, score, reason, status}]` (`services/adaptive.py:75-91`); API wrapper returns parsed JSON (`src/services/api.js:16`). Auth context actions return `{ success: true }` or `{ success: false, error }` (`src/context/AuthContext.jsx:58-86`).

## Module Design

**Exports:** Python modules export plain functions + module-level constants (`SPACED_INTERVALS`, `ROLES`, `TOPICS`, `SCENARIOS`, `CURATED_RESOURCES`); no classes except SQLAlchemy models and test `MockState`/`MockProfile`. JS `src/services/api.js` exports a single `api` object of arrow-function properties; components use `export default function <Name>`; context exposes `AuthProvider` + `useAuth()` hook (`src/context/AuthContext.jsx:6,153`).

**Barrel Files:** None. Import directly from the defining module (`from services.adaptive import ...`, `import { api } from '../services/api'`). Do not create `index.js` barrels.

---

*Convention analysis: 2026-09-25*
