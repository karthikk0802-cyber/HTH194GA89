# Golden KB eval set — guards SOP retrieval against regressions.
# After every ingest or SOP revision, these must still answer substantively.
# Offline-safe: asserts on answer substance, never on exact LLM wording.

GOLDEN_PAIRS = [
    ("What is the internet stipend at Nexora?", "$50"),
    ("When are production deployments scheduled?", "Tuesdays"),
    ("How often must passwords be rotated?", "90 days"),
    ("What branching methodology does engineering enforce?", "Trunk"),
    ("What is the core collaboration window?", "10:00 AM"),
    ("Where are expense receipts submitted?", "Expensify"),
    ("What language are backend microservices written in?", "Go"),
    ("What framework prioritizes features?", "RICE"),
    ("Which qualification framework do sales reps use?", "MEDDIC"),
    ("What is the Sev1 response SLA?", "15 minutes"),
]


def test_kb_golden_answers():
    from services.rag import generate_rag_response

    failures = []
    for query, must_contain in GOLDEN_PAIRS:
        res = generate_rag_response(query, role="all")
        answer = res.get("answer", "") or ""
        if len(answer) < 50 or "insufficient information" in answer.lower():
            failures.append(f"no substantive answer for: {query}")
        elif must_contain.lower() not in answer.lower():
            failures.append(f"missing '{must_contain}' for: {query}")
    assert not failures, "KB golden eval failures:\n" + "\n".join(failures)
