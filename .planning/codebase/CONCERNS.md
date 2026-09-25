---
last_mapped_commit: 39d2d8cb910ac84883ea29f2a4f16d44679d579e
last_mapped_at: 2026-09-25
---
# Codebase Concerns

**Analysis Date:** 2026-09-25

## Tech Debt

**God-file `server.py` (1399 lines, 40+ routes inline):**

- Issue: Every API route, Pydantic model, and piece of business logic (XP award, mastery updates, signoff checks, resume handling) lives in `server.py`. No routers, no service-layer separation for HTTP concerns.
- Files: `server.py` (lines 1–1399)
- Impact: Merge conflicts, untestable handlers, slow navigation. Adding any endpoint requires editing the same file.
- Fix approach: Split into `routers/auth.py`, `routers/quiz.py`, `routers/admin.py`, `routers/manager.py`, `routers/v2.py` with `APIRouter` and move Pydantic models to `schemas/`. Keep behavior identical per route.

**Bare `except Exception` + `print()` instead of logging (pervasive):**

- Issue: Dozens of `except Exception:` handlers either `pass` silently or `print()` a warning. No `logging` module anywhere in `services/`.
- Files: `server.py:99,577,870,885,950,967,1191,1201,1228,1269`, `services/quiz_generator.py:397,516`, `services/scenarios.py:119-120`, `services/embedding.py:95`, `services/llm.py:78`
- Impact: Silent failures (e.g., `log_seen` failures in `server.py:574-578,1225-1229,1266-1270` are swallowed with `pass`, so eval-unseen tracking silently stops working). Production has no log aggregation path.
- Fix approach: Introduce `logging.getLogger(__name__)` per module, log at `warning`/`exception` level, and only `pass` where the comment justifies it. Alert on `log_seen` failures.

**Deprecated `@app.on_event("startup")`:**

- Issue: `server.py:77` uses `@app.on_event("startup")`, removed in newer FastAPI/Starlette in favor of `lifespan`.
- Files: `server.py:77-100`
- Impact: Startup hook breaks on FastAPI upgrade; deprecation warnings today.
- Fix approach: Migrate to `@asynccontextmanager lifespan` and pass to `FastAPI(lifespan=...)`.

**Naive datetimes everywhere (`datetime.utcnow()` deprecated in Python 3.12+):**

- Issue: All timestamps use naive `datetime.utcnow()` while two sidecars use timezone-aware `datetime.now(timezone.utc)`. Mixing naive/aware datetimes raises `TypeError` on comparison.
- Files: `services/db.py:20,30,63`, `services/auth_db.py:24`, `services/adaptive.py:19,74`, `services/gamification.py:30`, `services/quiz_policy_v2.py:36`, `server.py:379-380,963` vs `services/resume_profile.py:127`, `services/eval_seen.py:33`
- Impact: `effective_mastery()` in `services/quiz_policy_v2.py:36-42` catches `TypeError` and returns undiscounted mastery — stale mastery silently treated as fresh. Future `TypeError` crashes wherever naive meets aware.
- Fix approach: Standardize on `datetime.now(timezone.utc)` everywhere; add a migration for stored naive values.

**Dual role/topic systems that diverge:**

- Issue: v1 `services/roles.py` (`ROLES`, `TOPICS`, `get_role_topics`) and v2 `services/taxonomy.py` (`ROLE_CARDS`, `get_role_card`) define overlapping but different role→topic mappings. `get_role_topics()` in `services/roles.py:25-38` only special-cases 4 roles and falls back to 3 base topics for everything else (e.g., `Marketing Specialist`, `HR Manager`, `Data Scientist` get a wrong 3-topic plan on v1 paths).
- Files: `services/roles.py`, `services/taxonomy.py`, `server.py:471-519` (v1) vs `server.py:1206-1233` (v2)
- Impact: Same user sees different required topics on `/api/learning-path` vs `/api/v2/quiz/next`; readiness scores disagree between dashboard and manager report.
- Fix approach: Make `get_role_topics()` delegate to `get_role_card()` with legacy alias mapping, or delete `services/roles.py` and migrate v1 callers.

**Manual SQLite schema patching instead of migrations:**

- Issue: Schema evolution is hand-rolled `sqlite3` `ALTER TABLE` in `services/db.py:69-90` (`ensure_schema`) and `services/auth_db.py:29-43` (`ensure_auth_schema`), plus `CREATE TABLE IF NOT EXISTS` in `services/resume_profile.py:35-48` and `services/eval_seen.py:17-25`.
- Files: `services/db.py`, `services/auth_db.py`, `services/resume_profile.py`, `services/eval_seen.py`
- Impact: No downgrade path, no migration history, column renames impossible, concurrent first-boot can race `create_all`.
- Fix approach: Adopt Alembic with a single migration chain; keep `ensure_*` as a one-version bridge.

**Repo hygiene — secrets-adjacent and generated files present, `.gitignore` incomplete:**

- Issue: `.gitignore` covers only logs, `node_modules`, `dist`, and editor files. It does NOT ignore `.env`, `*.db`, `*.bak`, `chroma_db/`, `__pycache__/`, `.pytest_cache/`. The repo root currently contains `.env`, `auth.db`, `auth.db.bak`, `onboardiq.db`, `onboardiq.db.bak`, `chroma_db/`, `__pycache__/`, `.pytest_cache/`, `dist/`, `graphify-out/`.
- Files: `.gitignore`, `.env` (existence only — contents never read), `auth.db`, `auth.db.bak`, `onboardiq.db`, `onboardiq.db.bak`, `chroma_db/`, `dist/`
- Impact: High risk of committing live credentials and user data (`*.db` holds password hashes, PII, quiz history). Bloated clones, accidental data leaks on every commit.
- Fix approach: Extend `.gitignore` with `.env*`, `*.db`, `*.bak`, `chroma_db/`, `__pycache__/`, `.pytest_cache/`, `graphify-out/`; untrack already-committed DBs with `git rm --cached`; rotate any credential that was ever committed.

## Known Bugs

**Admin KB endpoints missing auth — anyone can upload/toggle/delete docs:**

- Symptoms: `GET /api/admin/docs`, `POST /api/admin/docs/toggle/{id}`, `DELETE /api/admin/docs/{id}`, `POST /api/admin/docs/upload`, `GET /api/admin/feedback` have no `Depends(_admin_guard)`. Only `POST /api/admin/docs/approve/{id}` is guarded.
- Files: `server.py:831-931` (unguarded) vs `server.py:934` (guarded)
- Trigger: `curl -X DELETE localhost:8000/api/admin/docs/1` succeeds with no `Authorization` header.
- Workaround: None. Fix by adding `admin: str = Depends(_admin_guard)` to all five handlers.

**Frontend admin doc actions never send the admin token (approve always 403; upload works only because server is unguarded):**

- Symptoms: `approveDocument`, `toggleDocument`, `deleteDocument`, `uploadDocument`, `getDocuments`, `getFeedbackList` in `src/services/api.js:117-132` send no `Authorization` header, while the server's approve route demands one.
- Files: `src/services/api.js:117-132`, `src/pages/AdminCenter.jsx`, `server.py:854-934`
- Trigger: Click "Approve" in AdminCenter → 403 `Admin access required` every time.
- Workaround: None in UI; API works with `curl -H "Authorization: Bearer <admin_token>"`.

**Quiz submit trusts client-provided `correctAnswer` — score/XP forgeable:**

- Symptoms: `POST /api/quiz/submit` accepts both `selectedAnswer` and `correctAnswer` from the client and compares them (`server.py:581-617`). A user can send `selectedAnswer == correctAnswer == "anything"` and gain mastery + XP.
- Files: `server.py:581-617`, `src/services/api.js:67-71`
- Trigger: `POST /api/quiz/submit {"userId":"x","topicId":"security","selectedAnswer":"A","correctAnswer":"A"}` → `is_correct: true`, +15 XP.
- Workaround: Use the v2 graded eval (`/api/v2/eval/submit`), which grades server-side by `eval_id`. Fix by looking up the canonical answer server-side for v1 too.

**Single-question diagnostic bypass: one lucky guess completes a topic:**

- Symptoms: `get_diagnostic_questions_for_role()` in `services/diagnostic.py:255-302` seeds each role topic with exactly one question, and `evaluate_diagnostic()` in `services/diagnostic.py:355-360` bypasses any topic scored ≥80% — i.e., 1/1 correct bypasses. Only `security` is protected by `apply_bypass_policy()`.
- Files: `services/diagnostic.py:255-302,355-360`, `services/taxonomy.py:176-178`, `server.py:354-426`
- Trigger: Guess the single `company_basics` question right → `status=Completed, mastery=90`.
- Workaround: None. Fix by requiring ≥2 questions per topic before bypass, or raising the bypass threshold when sample size is 1.

**`update_badges` / dashboard crash on malformed `badges` JSON:**

- Symptoms: `json.loads(profile.badges)` in `services/gamification.py:44` and `server.py:718` has no `try/except`. A `NULL` or hand-edited `badges` value raises 500 on every quiz submit and dashboard load.
- Files: `services/gamification.py:42-62`, `server.py:700-737`
- Trigger: Set `user_profiles.badges = 'corrupt'` → dashboard and quiz submit 500.
- Workaround: Manually reset the column to `'[]'`. Fix with a `try/except json.JSONDecodeError` defaulting to `[]`.

**Streak logic never counts same-day activity and `delta.days` truncates:**

- Symptoms: `check_streak()` in `services/gamification.py:28-40` only increments when `delta.days == 1`; same-day repeat logins update `last_login` without incrementing, and a 25-hour gap reads as `delta.days == 1` (still counts). Naive datetimes compound DST errors.
- Files: `services/gamification.py:28-40`, `server.py:224-235`
- Trigger: Log in twice in one day → streak unchanged (arguably correct) but login at 11pm then 1am next day (`2h` apart, `delta.days == 0`) → streak not incremented despite consecutive calendar days.
- Workaround: None. Fix by comparing calendar dates in a fixed timezone.

**Non-deterministic recommendations (`random` without seed in request path):**

- Symptoms: `pick_next_topic()` in `services/quiz_policy_v2.py:45-56` uses `random.Random(None)` and a 70/30 coin flip, so `/api/v2/quiz/next` returns a different topic on every call for identical state.
- Files: `services/quiz_policy_v2.py:45-56`, `server.py:1205-1233`
- Trigger: Refresh the quiz page → "next topic" changes randomly.
- Workaround: None. Fix by ranking deterministically (weakest mastery first) and only randomizing ties with a user-scoped seed.

**Session IDs can collide (`time.time()` ms mod 1M + 3-digit rand):**

- Symptoms: `generate_quiz_session()` in `services/quiz_generator.py:401-410` builds `sess_{ms%1000000}_{100-999}` — ~1M × 900 space, no uniqueness check.
- Files: `services/quiz_generator.py:401-410`
- Trigger: Two sessions created in the same millisecond with the same rand → identical IDs.
- Workaround: None observed in practice. Fix with `uuid4().hex`.

## Security Considerations

**Forgeable token scheme (no JWT, no signature, prefix-only check on some paths):**

- Risk: User tokens are `token_{username}_{id}` and admin tokens `admin_token_{username}_{id}` — guessable, never expire, never verified against a session store. `is_admin_token()` in `services/admin_auth.py:14-20` accepts ANY string starting with `admin_token_` (the DB re-check in `require_admin` saves guarded routes, but `/api/auth/register`'s gate in `server.py:162-165` uses the prefix-only `is_admin_token`, so any `Bearer admin_token_anything` can create users).
- Files: `services/admin_auth.py:1-70`, `server.py:162-165,209,249,1041`
- Current mitigation: `require_admin` re-queries `auth.db` for `is_admin` on guarded admin routes; user tokens are effectively decorative on most routes.
- Recommendations: Replace with signed JWTs (expiry + secret from env), store sessions server-side or verify signature per request, and use `require_admin` (not `is_admin_token`) on the register gate.

**Most user-scoped endpoints trust client-supplied `userId` with zero token verification:**

- Risk: Dashboard, learning path, quiz submit, diagnostic evaluate, scenario evaluate, manager report, buddy attention, and both v2 eval endpoints accept a `userId` query/body field and return/mutate that user's data with no `Authorization` check. Any user can read or advance anyone else's record.
- Files: `server.py:311-334,355,432,470,548,581,654,700,742,797,1184-1349`, `src/context/AuthContext.jsx:88-92` (`quickSwitchUser` fabricates `token_{username}_{id}` client-side with no server round-trip)
- Current mitigation: None — `AuthContext` defaults to a hardcoded `sarah_engineer` demo user (`src/context/AuthContext.jsx:7-20`), so impersonation is one dropdown away by design (demo convenience).
- Recommendations: Require a verified session token on every user-scoped route; derive `userId` from the token, never from the request; remove `quickSwitchUser` forgery or gate it behind admin.

**Weak password hashing (SHA-256, single global static salt):**

- Risk: `hash_password()` in `services/auth_db.py:52-55` is `sha256("nexora_onboardiq_secure_salt_2026" + password)` — fast hash, same salt for every user, salt committed to source. Rainbow-table / GPU-brute-force friendly. Demo seeds use `password123` for 3 accounts (`services/auth_db.py:60-127`).
- Files: `services/auth_db.py:52-58`
- Current mitigation: None (no pepper rotation, no work factor).
- Recommendations: Migrate to `bcrypt`/`argon2` with per-user salts; force-reset the `password123` demo accounts; add login rate limiting (see below).

**CORS wildcard + credentials is a misconfiguration:**

- Risk: `allow_origins=["*"]` combined with `allow_credentials=True` in `server.py:68-74` — browsers reject this combination, so credentialed frontend calls behave inconsistently, and any tightening mistake exposes the API to any origin.
- Files: `server.py:67-74`
- Current mitigation: None.
- Recommendations: Set explicit origins from env (`FRONTEND_ORIGIN=http://localhost:5173` for dev) and keep `allow_credentials=True` only with that allowlist.

**No rate limiting on login, register, QA, or quiz endpoints:**

- Risk: `POST /api/auth/login`, `/api/admin/login`, `/api/qa/ask` (LLM cost), `/api/quiz/*` accept unlimited requests — credential stuffing and LLM-bill exhaustion.
- Files: `server.py` (all routes; no middleware for throttling)
- Current mitigation: None.
- Recommendations: Add `slowapi` (or reverse-proxy limits): strict limits on auth routes (e.g., 5/min/IP), looser on QA/quiz.

**Tokens and PII in `localStorage` (XSS theft):**

- Risk: Auth tokens and full user objects persist in `localStorage` (`src/context/AuthContext.jsx:20,43,52`, `src/pages/AdminLogin.jsx:16-17`, `src/pages/UserManagement.jsx:8`). Any XSS payload exfiltrates sessions.
- Files: `src/context/AuthContext.jsx`, `src/pages/AdminLogin.jsx:16-17`, `src/App.jsx:28`
- Current mitigation: None (no CSP headers observed; API base is hardcoded `http://localhost:8000` in `src/services/api.js:1`).
- Recommendations: Move tokens to `httpOnly` cookies, add CSP headers, and stop storing the full user object client-side.

**Unbounded file upload (no size/type validation, filename trusted):**

- Risk: `/api/admin/docs/upload` (`server.py:892-931`) and `/api/v2/profile/resume` (`server.py:1358-1378`) read the entire file into memory, accept any extension (`extract_text` in `services/document_processor.py:6-19` silently returns `""` for unknown types but the doc row + Chroma entries are still created), and persist `file.filename` verbatim. No max size → zip-bomb / OOM via crafted PDF/DOCX; no MIME check → executable uploads stored as metadata.
- Files: `server.py:892-931,1358-1378`, `services/document_processor.py:6-19`
- Current mitigation: Resume route is admin-guarded; docs upload is (incorrectly) unguarded — see bug above.
- Recommendations: Enforce max size (e.g., 10 MB) at the FastAPI layer, allowlist extensions/MIME types, sanitize filenames, and skip DB/Chroma writes when extracted text is empty.

**RAG prompt injects raw user query into the LLM system prompt:**

- Risk: `generate_rag_response()` in `services/rag.py:77-91` interpolates `clean_query` directly into the coach prompt. Crafted queries can override instructions ("ignore previous instructions…").
- Files: `services/rag.py:77-91`, `services/scenarios.py:65-95`, `services/quiz_generator.py:367-374,473-494`
- Current mitigation: Low temperature (0.3) and evidence-grounded wording reduce but do not prevent injection.
- Recommendations: Delimit untrusted input with explicit tags, add an instruction-hierarchy preamble, and cap query length (Pydantic `Field(max_length=…)`).

**PII enumeration via unauthenticated buddy/manager endpoints:**

- Risk: `GET /api/buddy/{username}/attention` (`server.py:742-758`) and `GET /api/manager/team` (`server.py:760-795`) require no auth and disclose usernames, full names, roles, and per-topic mastery for arbitrary users.
- Files: `server.py:742-795`
- Current mitigation: None.
- Recommendations: Guard both with session auth and scope buddy queries to the caller's own learners.

**Pydantic models lack input constraints:**

- Risk: `RegisterRequest`, `LoginRequest`, `QARequest`, and others in `server.py:105-156` have no `Field(min_length/max_length/pattern)`; `email` is a bare `str` (not `EmailStr`); `query` is unbounded (LLM cost / DoS); `role`/`department` accept arbitrary strings persisted to the DB.
- Files: `server.py:105-156,995-1015,1148-1150,1273-1282`
- Current mitigation: `change-password` checks length ≥ 8 (`server.py:284`).
- Recommendations: Add `Field` constraints, `EmailStr` for emails, and role allowlists validated against `ROLE_CARDS`.

## Performance Bottlenecks

**Synchronous blocking handlers for embedding/LLM/Chroma work:**

- Problem: All route handlers are sync `def` and call blocking ChromaDB queries, `sentence-transformers` encoding, and Mistral HTTP inline (e.g., quiz generation, RAG ask, scenario eval). Each occupied worker blocks the event loop thread.
- Files: `server.py:524-527,532-546,654-685`, `services/embedding.py:6-18`, `services/llm.py:36-79`, `services/rag.py:42`
- Cause: No `async def` + threadpool offload; first Chroma call also cold-loads the `BAAI/bge-small-en-v1.5` model inside the request.
- Improvement path: Make I/O-bound routes `async def` with `run_in_executor` for embedding/LLM calls, warm the embedding model at startup (lifespan), and add request timeouts.

**Manager team endpoint is N+1 (full table scans per member):**

- Problem: `get_manager_team()` loads all profiles, then issues one `UserTopicState` query per user plus per-user `compute_readiness` (`server.py:760-795`). 100 users → 100+ queries per page load.
- Files: `server.py:760-795`
- Cause: No eager loading / single `WHERE user_id IN (...)` batch fetch.
- Improvement path: One batched states query grouped by `user_id`; add pagination (`limit`/`offset`) and cache readiness for 60s.

**Chroma search over-fetches 3× and filters in Python:**

- Problem: `search_chroma()` fetches `min(n_results*3, 30)` candidates then discards drafts/inactive client-side (`services/embedding.py:29-69`). Quiz generation calls it 1× per question plus extra LLM round-trips.
- Files: `services/embedding.py:29-69`, `services/quiz_generator.py:437-445`, `services/rag.py:42`
- Cause: Lifecycle status is a metadata tag filtered post-query instead of a native `where` clause.
- Improvement path: Push `status` into the Chroma `where` filter; backfill legacy chunks missing the key (they currently default to visible).

**Global Chroma collection singleton with no lock, re-created per process:**

- Problem: `_collection` module-global in `services/embedding.py:4-18` is lazily created with no thread lock; concurrent first requests can double-initialize the persistent client.
- Files: `services/embedding.py:4-18,88-98`
- Cause: Check-then-act race on `_collection is None`.
- Improvement path: Guard with `threading.Lock` or initialize eagerly in lifespan.

**Quiz session validation fans out to the LLM per question:**

- Problem: `get_quiz_session()` (`server.py:548-579`) and `v2_quiz_session()` (`server.py:1249-1271`) call `validate_quiz_question()` per question, which — when a Mistral key is configured — makes one LLM call per question (20 LLM calls per 20-question session) via `services/quiz_validator.py:36-53`.
- Files: `server.py:548-579,1249-1271`, `services/quiz_validator.py:20-54`
- Cause: Tier-2 LLM audit runs inline in the request path with no batching.
- Improvement path: Validate once per batch, run Tier-2 asynchronously after serving the (Tier-1-passed) session, or cache verdicts by question hash.

## Fragile Areas

**Auth module (`services/auth_db.py` + `services/admin_auth.py` + auth routes):**

- Files: `services/auth_db.py`, `services/admin_auth.py`, `server.py:161-334,1029-1146`, `src/context/AuthContext.jsx`, `src/pages/AdminLogin.jsx`
- Why fragile: Three token flavors (`token_*`, `admin_token_*`, `demo_token`), import-time side effects (`seed_default_auth_users()` at import, `ensure_admin_seed()` at import in `server.py:51`), and `ensure_admin_seed()` overwriting the admin password hash from env on every boot (`services/admin_auth.py:113-115`). Changing any piece locks out admins or demo users.
- Safe modification: Change one seam at a time (token format, seed behavior, guard) with a manual login-matrix test (user login, admin login, expired admin demotion, fresh-clone seed). Never edit seed + guard in the same change.
- Test coverage: Only hash round-trip + user-count tests (`tests/test_core_logic.py:278-292`). Zero endpoint/auth-flow tests.

**Adaptive mastery state machine (`services/adaptive.py` + diagnostic writer):**

- Files: `services/adaptive.py`, `server.py:354-426` (diagnostic evaluate), `server.py:581-617` (quiz submit), `server.py:933-972` (approve invalidation), `services/quiz_policy_v2.py`
- Why fragile: Thresholds are duplicated in three places (`adaptive.py:28-33` vs `quiz_policy_v2.py:8-18` vs `readiness.py:20-36`); diagnostic evaluate writes `Completed/Expert/90` directly instead of calling `update_topic_state`; approve-time invalidation flips all `Completed` rows for a topic without touching `mastery_score`, leaving score/status inconsistent.
- Safe modification: Route all state transitions through `update_topic_state()`; add a transition-table unit test before touching thresholds; keep v1 thresholds frozen when editing v2.
- Test coverage: Good unit coverage of `update_topic_state`/`rank_next_topics` (`tests/test_core_logic.py:88-137`) but no integration test of diagnostic→state→readiness.

**ChromaDB lifecycle (draft/active/inactive filtering):**

- Files: `services/embedding.py`, `server.py:854-972`, `services/rag.py`, `services/quiz_generator.py:437-462`
- Why fragile: Visibility depends on a `status` metadata tag backfilled only for docs touched since the feature; legacy chunks without the key are treated as visible by convention (`services/embedding.py:52`). `set_document_status` builds chunk IDs as `doc_{id}_chunk_{i}` for `range(chunk_count)` — if `chunk_count` drifted from reality, some chunks keep stale status and leak drafts into RAG/quiz context.
- Safe modification: Reconcile `chunk_count` against actual Chroma IDs before status flips; verify with a draft-visibility test (upload → ask → assert no leak → approve → ask → assert visible).
- Test coverage: None — no test covers `set_document_status`, `search_chroma` filtering, or the approve flow.

**Baseline/eval question-bank ID scheme (`eval_id = topic:idx`):**

- Files: `services/quiz_generator.py:248-320`, `server.py:1309-1349`, `services/eval_seen.py`
- Why fragile: Stable grading IDs are positional indices into `_full_static_bank(topic)`. Appending/reordering `FALLBACK_QUIZ_BANK` or `BANK_EXTRA` renumbers every `eval_id` after the edit point, so previously served evals grade against the wrong answer key.
- Safe modification: Never reorder existing bank entries — append only; better, migrate to content-hash IDs (`qhash`) with a stored answer map.
- Test coverage: Session uniqueness is tested (`tests/test_core_logic.py:361-376`); eval grading stability across bank edits is not.

**Resume profile calibration (`services/resume_profile.py`):**

- Files: `services/resume_profile.py`, `server.py:1205-1233,1358-1395`
- Why fragile: Keyword-substring matching (`"go "` with trailing space, `"aws"` matches `"laws"`-style collisions, `"scrum"`-style generic hits) drives `start_difficulty` floors; `years` is `max()` of every `\d+ years` mention (a "10+ years of company history" sentence inflates seniority). Raw SQL with `sqlite3` bypasses the SQLAlchemy engine (two connection pools to the same file).
- Safe modification: Tighten matching to word boundaries, cap `years_overall` plausibility, and reuse `SessionLocal` instead of raw `sqlite3.connect`.
- Test coverage: None — no test for `extract_profile`, `map_to_role_card`, or the resume endpoints.

## Scaling Limits

**SQLite (two files, same-process connections):**

- Current capacity: Single-server demo; `auth.db` + `onboardiq.db` with `check_same_thread=False` (`services/auth_db.py:9`, `services/db.py:7`).
- Limit: Write lock contention under concurrent quiz submits; no replication; `.bak` copies suggest manual backup. Breaks past a handful of concurrent writers or any multi-instance deploy.
- Scaling path: Migrate to PostgreSQL (SQLAlchemy URLs already centralized); keep SQLite for local dev via env-switched `DATABASE_URL`.

**Local ChromaDB + in-process sentence-transformers:**

- Current capacity: `chroma_db/` on local disk, `BAAI/bge-small-en-v1.5` loaded in-process (`services/embedding.py:12`).
- Limit: Disk size and RAM of one box; model load stalls first requests for tens of seconds; no shared index across instances.
- Scaling path: External vector store (managed Chroma/pgvector) + dedicated embedding service with caching; pre-warm at startup.

**LLM dependency (Mistral API or keyword fallback):**

- Current capacity: Direct per-request Mistral calls with 5-model fallback chain (`services/llm.py:42-45`); offline keyword fallback returns canned answers.
- Limit: API quota/rate limits and per-request latency bound `/api/qa/ask`, quiz generation, and scenario eval throughput. Fallback answers are static and quickly stale.
- Scaling path: Response caching by (query, role) hash, background pre-generation of quiz banks, and circuit-breaker to fallback with metrics.

## Dependencies at Risk

**`sentence-transformers` / `torch` (heavy, unpinned):**

- Risk: `requirements.txt:13` declares `sentence-transformers>=2.6.1` unbounded — pulls `torch` (~800MB+) and breaks across versions; model download (`BAAI/bge-small-en-v1.5`) happens at runtime, failing offline first-boots.
- Impact: Fresh `pip install` is slow/fragile; CI and deploys non-reproducible; first RAG/quiz request hangs on model fetch.
- Migration plan: Pin exact versions in `requirements.txt` (or lock with `pip-compile`/`uv`), vendor or pre-download the model in the build, and lazily degrade to keyword search with a logged warning when the model is absent.

**Unpinned backend requirements overall:**

- Risk: Every line in `requirements.txt` is `>=` unbounded (`fastapi>=0.110.0`, `chromadb>=0.4.24`, `mistralai>=0.1.3`, …). The deprecated `@app.on_event` already signals version drift exposure.
- Impact: Any fresh install can silently upgrade FastAPI/Chroma/Mistral past breaking changes.
- Migration plan: Pin `==` versions verified against the test suite; add a weekly Dependabot-style bump with `pytest` gating.

**Frontend on React 19 + Vite 8 bleeding edge with no tests:**

- Risk: `package.json` uses `react@^19.2.8`, `vite@^8.3.0` with caret ranges and zero frontend tests or type checking.
- Impact: Minor-version bumps can break the UI with no safety net (e.g., `AdminCenter` already broken against its own backend — see bugs).
- Migration plan: Lock `package-lock.json` in CI (`npm ci`), add smoke tests for login → dashboard → quiz flows, and pin major versions.

## Missing Critical Features

**No authorization enforcement on user-scoped reads/writes:**

- Problem: There is authentication (login issues a token) but almost no authorization (the token is never validated on user routes). Any client can act as any user.
- Blocks: Any production or pilot deployment with real employee data; SOC 2 / compliance review.

**No audit trail for privileged actions:**

- Problem: Admin user CRUD, baseline resets, role transfers, doc approve/delete, signoffs, and resume uploads write no audit log (who did what, when). `SignoffModel` records the claimed `signer` string from the request body (`server.py:1284-1304`) with no proof the signer approved.
- Blocks: Compliance accountability, incident forensics, dispute resolution over certifications.

**No automated tests for the HTTP layer or frontend:**

- Problem: 4 test files cover pure service functions only; `server.py` (the largest file), all auth flows, the frontend, and the Chroma lifecycle have zero tests. No CI config exists.
- Blocks: Safe refactoring of any fragile area above; every fix risks silent regression.

## Test Coverage Gaps

**HTTP endpoints (`server.py`, ~1400 lines, 40+ routes):**

- What's not tested: Every route — auth login/register/change-password, diagnostic evaluate, quiz session/submit, scenario evaluate, dashboard, manager team/report, admin docs CRUD/approve, v2 baseline/eval, resume upload, signoff.
- Files: `server.py`
- Risk: The cheat-via-`correctAnswer` bug, the missing admin guards, and the approve-403-from-UI bug all survive because no test ever calls the API.
- Priority: High

**Auth and admin-guard matrix:**

- What's not tested: Token forgery rejection, `is_admin_token` prefix bypass on register, `require_admin` DB re-check, self-delete guard, buddy-vs-admin signoff rules.
- Files: `services/admin_auth.py`, `services/auth_db.py`, `server.py:161-334,1029-1146`
- Risk: Auth regressions deploy silently; privilege escalation unnoticed.
- Priority: High

**ChromaDB lifecycle and RAG grounding:**

- What's not tested: Draft invisibility, toggle/approve/delete propagation to search results, `chunk_count` drift, role filtering, evidence-confidence thresholds.
- Files: `services/embedding.py`, `services/rag.py`, `server.py:854-972`
- Risk: Draft SOPs leaking into employee answers, or approved docs invisible to RAG.
- Priority: High

**Eval stability and seen-tracking:**

- What's not tested: `build_graded_eval`/`grade_graded_eval` unseen-only guarantee, `log_seen`/`get_seen_hashes` round-trip, grading stability when the bank grows.
- Files: `services/quiz_generator.py:252-320`, `services/eval_seen.py`, `server.py:1309-1349`
- Risk: Practice questions leaking into graded evals (inflated certifications); bank edits silently re-keying eval answers.
- Priority: Medium

**Resume calibration and frontend flows:**

- What's not tested: `extract_profile`/`map_to_role_card`/`save_profile`, resume upload endpoint, and all React pages/components (no runner configured — `package.json` has no test script).
- Files: `services/resume_profile.py`, `src/pages/`, `src/components/`, `src/context/AuthContext.jsx`
- Risk: Keyword false-positives miscalibrating new hires; UI/backend contract drift (already happened with admin tokens).
- Priority: Medium

---

*Concerns audit: 2026-09-25*
