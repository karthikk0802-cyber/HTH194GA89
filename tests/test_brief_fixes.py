# Brief-gap fixes: grounded fallback, daily plan shape. Offline-safe.

from fastapi.testclient import TestClient


def _bank_texts():
    from services.quiz_generator import FALLBACK_QUIZ_BANK
    from services.question_bank import BANK_EXTRA
    return {i["question"] for v in list(FALLBACK_QUIZ_BANK.values()) + list(BANK_EXTRA.values()) for i in v}


def test_grounded_fallback_never_synthesizes():
    from services.quiz_generator import grounded_fallback_question
    banked = _bank_texts()
    for topic in ["Company Basics", "Deployment & CI/CD", "Sales Playbook",
                  "Product Triage", "Security & Compliance"]:
        q = grounded_fallback_question(topic)
        assert "error" not in q, topic
        assert q["question"] in banked, f"ungrounded output for {topic}"
        assert q["correct_answer"] in q["options"]


def test_today_plan_shape():
    import server
    client = TestClient(server.app)
    res = client.get("/api/plan/today", params={"userId": "sarah_engineer",
                                                "role": "Software Engineer"})
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body["items"], list)
    assert body["total_minutes"] == sum(i["minutes"] for i in body["items"])
    for item in body["items"]:
        assert item["kind"] in ("focus", "review", "stretch")
        assert item["minutes"] > 0 and item["reason"]
