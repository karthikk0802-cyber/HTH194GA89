# Solid Plan — Admin Portal + Adaptive Quiz v2 (Blast-Radius Safe)

Rule for everything below: **freeze the 5 contracts, add beside them, verify before proceeding.**
Nothing gets edited in place.

## Frozen contracts (do not touch)

1. `server.py:262-263` `GET /api/diagnostic/questions` → `diagnostic.py:255`
   `get_diagnostic_questions_for_role(role,count)`.
   `PreAssessment.jsx:20` expects `[{id, topic, topic_title, question, options}]`.
2. `server.py:267` `POST /api/diagnostic/evaluate` → `diagnostic.py:304`
   `evaluate_diagnostic(answers,role)`.
   `PreAssessment.jsx:49,130-181` expects
   `{correct_count, total_questions, score_percentage, xp_gained, total_xp,
   level, bypassed_titles, evaluations[]}`.
3. `server.py:399` `GET /api/quiz/generate` → `quiz_generator.py:203`
   `generate_quiz_for_topic(topic,role,difficulty)`.
   `QuizPractice.jsx:64` expects
   `{question, options, correct_answer, learning_objective, evidence_quote,
   citations, validation_passed}`.
4. `server.py:434` `POST /api/quiz/submit` → `adaptive.py:17`
   `update_topic_state(state,is_correct)`.
   Writes `mastery_score/difficulty/status/next_review_at` consumed by
   dashboard, manager team, readiness.
5. `server.py:356,373` `GET /api/learning-path` → `adaptive.py:62`
   `rank_next_topics()` + `build_competency_graph()`.
   `LearningPath.jsx` expects `{ranked_topics, competencies[], graph_edges[]}`.

No signature changes to `get_diagnostic_questions_for_role`,
`evaluate_diagnostic`, `generate_quiz_for_topic`, `update_topic_state`,
`rank_next_topics`, `build_competency_graph`. No DB column alterations —
only nullable additions.

## Phase 0 — Freeze + baseline (30 min, no behavior change)

1. Backup: `cp auth.db auth.db.bak`, `cp onboardiq.db onboardiq.db.bak`,
   `git status` clean, new branch `feat/admin-adaptive-safe`.
2. Capture contract fixtures — record current responses (save outputs,
   don't change code):
   - `GET /api/diagnostic/questions?role=Software%20Engineer&count=10`
   - `POST /api/diagnostic/evaluate` with a fixed answer set
   - `GET /api/quiz/generate?topic=Company%20Basics&role=all&difficulty=Beginner`
   - `GET /api/learning-path/demo_user?role=Software%20Engineer`
   - `pytest tests/test_core_logic.py -q` — must be green before starting;
     if red, stop.
3. Read-only checks before coding: `services/db.py` `UserTopicState` columns,
   `services/embedding.py` `role_filter`, `services/llm.py` key handling,
   `.env` keys present.
4. Freeze list (no edits, only calls into): `diagnostic.py:255,304`,
   `quiz_generator.py:203`, `adaptive.py:17,62`, `build_competency_graph`,
   `server.py:262,267,356,399,434` handlers, `PreAssessment.jsx`,
   `QuizPractice.jsx`, `LearningPath.jsx` data shapes.

Exit gate: fixtures saved + tests green. Rollback: n/a (nothing changed).

## Phase A — Admin portal (backend append-only + frontend hide)

### A1. Backend (only append to `server.py`, new file `services/admin_auth.py`)

- New `services/admin_auth.py`:
  `require_admin()` checks `Authorization: Bearer admin_token_...`;
  `ensure_admin_seed()` reads `ADMIN_USERNAME` + `ADMIN_PASSWORD_HASH` from
  env, creates/updates `UserAuthModel(is_admin=True)` via existing
  `hash_password()`. No plaintext password in code. Fail closed if env missing.
- New routes only:
  `POST /api/admin/login`,
  `GET /api/admin/users`, `POST /api/admin/users`,
  `PUT /api/admin/users/{username}`, `DELETE /api/admin/users/{username}`.
  Create path reuses `RegisterRequest` + cascade-creates `UserProfileModel`;
  delete path deletes `UserTopicState` + `UserProfileModel` rows for that
  user only. All guarded by `require_admin()`.
- Harden without deleting: `POST /api/auth/register` and
  `GET /api/auth/users` keep signatures, add `require_admin()` gate →
  non-admin gets `403 "disabled — contact admin"`.
- `auth_db.py` seed: replace hardcoded `admin123` with env hash; keep all
  other demo rows unchanged.

### A2. Frontend (new pages + flags, no edits to quiz pages)

- New `AdminLogin.jsx` at separate path (e.g. `/admin-login`), new
  `UserManagement.jsx` (list/create/edit/reset-baseline/delete).
- New `api.js` functions `admin*` only — existing
  `login/register/getUsers` untouched.
- `Login.jsx`: gate Create Account tab + Quick Demo block behind
  `VITE_ENABLE_DEMO_LOGIN` (default `false`); code stays, UI hides.
- `AuthContext.jsx`: keep `register()`/`quickSwitchUser()` exports
  (imported elsewhere), just remove call sites.
- `App.jsx`/`Sidebar.jsx`: show `admin-users` tab only if
  `user.is_admin && token.startswith("admin_token_")`.
- New `POST /api/admin/users/{u}/reset-baseline` deletes only that user's
  `UserTopicState` rows — the single admin→quiz seam. Admin never writes
  quiz content; quiz never writes auth.

Exit gate: admin login works via env; user token on `/api/admin/*` → 403;
public register → 403; v1 fixtures from Phase 0 byte-identical except
register/users gating; `pytest` green.
Rollback: set flags back, delete `/api/admin/*` routes — v1 untouched.

## Phase B — Adaptive quiz v2 (sidecars + v2 endpoints, v1 frozen)

### B1. Taxonomy data file (new `services/taxonomy.py` only)

- Format: `DEPARTMENTS = {"Engineering": ["Software Engineer", ...]}`,
  `ROLE_BASELINE = {role: [topics]}`, `GENERAL` vs `DEEP` tags.
- `roles.py` untouched — v2 reads taxonomy, v1 never imports it.
- Input needed: real department → role list.

### B2. Sidecar services (new files, wrap v1, never edit v1)

- New `services/baseline_v2.py`:
  `get_baseline_questions(role, per_topic=3)` calls v1
  `get_diagnostic_questions_for_role()` then groups — returns same item
  shape + `phase:"baseline"`.
  `score_baseline(answers)` calls v1 `evaluate_diagnostic()` and returns
  **all v1 keys with identical values** + additive `topic_scores`,
  `weak_topics`, `strong_topics`.
- New `services/quiz_policy_v2.py`:
  `pick_difficulty(mastery)` mirrors `adaptive.py` thresholds read-only;
  `pick_next_topic()` weakness-weighted (70% weak / 30% review);
  `generate_personalized_quiz()` calls v1 `generate_quiz_for_topic()`
  then adds `personalization:{reason}` without altering quiz fields.
- Persistence: no `ALTER` on `UserTopicState`. If needed, new nullable
  table `user_baseline_v2` — v1 code never reads it.

### B3. v2 endpoints (append to `server.py`)

- `GET /api/v2/diagnostic/questions`,
  `POST /api/v2/diagnostic/evaluate`,
  `GET /api/v2/quiz/next`,
  `GET /api/v2/quiz/generate`.
- Request bodies mirror v1; responses = v1 fields + extras.
- v1 handlers byte-identical.
- New `PreAssessmentV2.jsx` / `QuizPracticeV2.jsx` call `/api/v2/*`
  behind `VITE_QUIZ_V2` (default off). Old pages keep calling v1.

Exit gate: contract test asserts every v1 key present and equal in v2
responses; Phase 0 fixtures still pass against v1; `pytest` green;
manual script: new user → 3/topic baseline → weak list correct →
`/v2/quiz/next` favors weak.
Rollback: flag off, drop v2 routes — v1 never changed.

## Order + guarantees

Phase 0 → A → re-verify fixtures → B → re-verify fixtures.
Any gate fails: stop, roll back that phase only (flags + route deletion).
No step edits a frozen function, shape, or existing DB column, so blast
radius is limited to new code paths.

Open inputs: real department → role list, and whether demo accounts stay
behind a flag or get deleted.
