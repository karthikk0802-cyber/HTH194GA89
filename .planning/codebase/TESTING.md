---
last_mapped_commit: 39d2d8cb910ac84883ea29f2a4f16d44679d579e
last_mapped_at: 2026-09-25
---
# Testing Patterns

**Analysis Date:** 2026-09-25

## Test Framework

**Runner:**

- `pytest` >= 8.1.1 (`requirements.txt:14`)
- Config: no `pytest.ini` / `pyproject.toml` / `setup.cfg` — default rootdir discovery; tests live in `tests/`
- Frontend: no JS test runner (no `vitest`, `jest`, `@testing-library` in `package.json`)

**Assertion Library:**

- Plain `assert` statements (pytest rewriting). No `unittest.TestCase` classes.

**Run Commands:**

```bash
python -m pytest tests/ -v          # Full suite (see run.bat:8)
pytest tests/test_core_logic.py -q   # Single file, quiet (see plan.md:44)
pytest tests/test_kb_golden.py -q    # Golden KB eval only
pytest tests/test_concept_fixes.py tests/test_brief_fixes.py -q  # Regression slice
```

## Test File Organization

**Location:**

- Separate `tests/` directory (not co-located). Backend-only; no `src/**/*.test.*` files exist.

**Naming:**

- `tests/test_<area>.py`: `test_core_logic.py` (broad service suite), `test_kb_golden.py` (retrieval eval), `test_brief_fixes.py` (grounded fallback + plan shape), `test_concept_fixes.py` (bypass policy, held-out eval, decay). Package marker `tests/__init__.py` present.

**Structure:**

```
tests/
├── __init__.py
├── test_core_logic.py     # 30+ tests: chunking, roles/graph, adaptive, diagnostic, readiness, gamification, RAG, scenarios, auth, quiz diversity
├── test_kb_golden.py      # 10-pair SOP retrieval eval via live RAG
├── test_brief_fixes.py    # grounded_fallback_question + GET /api/plan/today shape
└── test_concept_fixes.py  # bypass policy, baseline scoring, graded eval, mastery decay, seen-tracking
```

## Test Structure

**Suite Organization:**

```python

# tests/test_core_logic.py:1-35 — imports first, then local doubles, then grouped tests

import pytest
import json
from datetime import datetime, timedelta
from services.document_processor import chunk_text, extract_metadata_from_text, extract_text
from services.adaptive import build_competency_graph, update_topic_state, rank_next_topics, SPACED_INTERVALS
...

# Mock State for testing

class MockState:
    def __init__(self, t_id, mastery=0, diff="Beginner", status="Locked"):
        self.topic_id = t_id
        self.mastery_score = mastery
        ...

# -------------------------------------------------------------

# 3. Adaptive Difficulty & Spaced Repetition Tests

# -------------------------------------------------------------

def test_adaptive_difficulty_progression():
    state = MockState("test", mastery=65, diff="Intermediate", status="Current")
    updated = update_topic_state(state, is_correct=True)
    assert updated.mastery_score == 75
    assert updated.difficulty == "Intermediate"
```

**Patterns:**

- Section-banner comments group tests by subsystem (`# 1. Document Processor Tests #`, `# 6. Gamification System Tests #` in `tests/test_core_logic.py`).
- Arrange-act-assert in one flat function; multiple asserts per test are normal (e.g. `test_readiness_evaluation` covers NOT YET READY / READY WITH GAPS / READY in one function, `tests/test_core_logic.py:172-189`).
- Function-local imports for heavy/optional deps to keep collection light:
  ```python
  # tests/test_core_logic.py:279
  def test_auth_password_hashing_and_verification():
      from services.auth_db import hash_password, verify_password, AuthSessionLocal, UserAuthModel
  ```

## Mocking

**Framework:** No `unittest.mock` / `pytest-mock` / ` responses` usage detected. Isolation is via hand-written fakes and real offline banks.

**Patterns:**

```python

# tests/test_core_logic.py:17-35 — duck-typed ORM doubles (attribute-compatible with SQLAlchemy models)

class MockState:
    def __init__(self, t_id, mastery=0, diff="Beginner", status="Locked"):
        self.topic_id = t_id
        self.mastery_score = mastery
        self.difficulty = diff
        self.status = status
        self.last_attempt_at = None
        self.next_review_at = None
        self.review_interval_days = 1

# tests/test_concept_fixes.py:72-80 — tmp_path fixture + module-global swap with restore

def test_seen_tracking_roundtrip(tmp_path):
    import services.eval_seen as es
    es.SEEN_DB = str(tmp_path / "seen.db")
    try:
        assert es.log_seen("u1", ["What is X?", "What is Y?"]) == 2
        ...
    finally:
        es.SEEN_DB = "./onboardiq.db"
```

**What to Mock:**

- ORM rows with `MockState` / `MockProfile` (attribute-compatible fakes) when testing pure logic (`adaptive`, `readiness`, `gamification`).
- Time with real `datetime.utcnow()` ± `timedelta` (no freezegun) — e.g. `state_rev.next_review_at = now - timedelta(hours=1)` (`tests/test_core_logic.py:89-96`).
- Filesystem/DB paths with pytest's built-in `tmp_path` (seen-tracking DB override above).

**What NOT to Mock:**

- Static question banks and service functions: call `generate_quiz_for_topic`, `generate_quiz_session`, `generate_rag_response`, `evaluate_diagnostic`, `score_baseline` for real (`tests/test_core_logic.py:331-376`).
- FastAPI app: use the real `server.app` via `TestClient` for contract tests (`tests/test_brief_fixes.py:23-34`).
- ChromaDB/LLM in golden tests: `test_kb_golden.py` hits the real retrieval path; it asserts on substance, never exact wording.

## Fixtures and Factories

**Test Data:**

```python

# tests/test_kb_golden.py:5-16 — golden Q/A pairs: query + must-contain substring

GOLDEN_PAIRS = [
    ("What is the internet stipend at Nexora?", "$50"),
    ("When are production deployments scheduled?", "Tuesdays"),
    ("How often must passwords be rotated?", "90 days"),
    ...
]

# tests/test_core_logic.py:142-144 — derive perfect answers from the source of truth

perfect_answers = {q["id"]: q["answer"] for q in DIAGNOSTIC_QUESTIONS}
res = evaluate_diagnostic(perfect_answers)
```

**Location:**

- Inline at top of the test file (`GOLDEN_PAIRS` in `tests/test_kb_golden.py`; `MockState`/`MockProfile` in `tests/test_core_logic.py`). No shared `conftest.py` or `fixtures/` directory — copy the 10-line mock class into a new file if needed.

## Coverage

**Requirements:** None enforced (no `--cov`, no `codecov`, no fail-under gate).

**View Coverage:**

```bash
pip install pytest-cov
python -m pytest tests/ --cov=services --cov-report=term-missing -q
```

## Test Types

**Unit Tests:**

- Scope: pure service logic — chunking/metadata (`test_chunking_logic`, `test_metadata_extraction*`), role graph (`test_roles_and_topics`, `test_competency_graph_edges`), adaptive progression/regression/intervals, diagnostic scoring, readiness states, XP/level/streak/badges, resources/voice/RAG confidence, password hashing (`tests/test_core_logic.py:40-283`). Fast, offline, deterministic.

**Integration Tests:**

- Scope: cross-module and HTTP contracts — `TestClient(server.app)` GET `/api/plan/today` shape (`kind in ("focus","review","stretch")`, `total_minutes` sum in `tests/test_brief_fixes.py:23-34`); live `auth.db` isolation count query (`tests/test_core_logic.py:285-292`); end-to-end quiz session generation across 8 topics × 20 questions with uniqueness + option-validity asserts (`tests/test_core_logic.py:361-376`); graded-eval build/grade round-trip including compliance-miss blocks-certification (`tests/test_concept_fixes.py:30-59`).

**E2E Tests:**

- Not used. No Playwright/Cypress/Selenium; frontend (`src/`) has zero automated tests. Verify UI manually via `npm run dev` (Vite `:5173`) against `uvicorn server:app`.

## Common Patterns

**Async Testing:**

```python

# Not used — backend services and endpoints under test are synchronous.

# Frontend async (fetch/Promise.all in src/pages/Dashboard.jsx:16-29) has no test coverage.

```

**Error Testing:**

```python

# tests/test_core_logic.py:125-130 — drive the failure branch, assert degraded-but-valid state

def test_adaptive_incorrect_answer_regression():
    state = MockState("test", mastery=45, diff="Intermediate", status="Current")
    updated = update_topic_state(state, is_correct=False)
    assert updated.mastery_score == 30
    assert updated.difficulty == "Beginner"

# tests/test_kb_golden.py:19-30 — collect all failures, assert once with a joined message

failures = []
for query, must_contain in GOLDEN_PAIRS:
    res = generate_rag_response(query, role="all")
    answer = res.get("answer", "") or ""
    if len(answer) < 50 or "insufficient information" in answer.lower():
        failures.append(f"no substantive answer for: {query}")
    elif must_contain.lower() not in answer.lower():
        failures.append(f"missing '{must_contain}' for: {query}")
assert not failures, "KB golden eval failures:\n" + "\n".join(failures)
```

**Offline-safety rule (follow for every new test):** assert on answer substance (`len(answer) > 50`, key fact present, `"insufficient information" not in answer.lower()`), never on exact LLM wording — see file headers in `tests/test_kb_golden.py:1-3` and `tests/test_concept_fixes.py:1-2`.

---

*Testing analysis: 2026-09-25*
