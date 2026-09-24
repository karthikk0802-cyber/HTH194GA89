# Regression tests for concept fixes: bypass policy, held-out eval,
# mastery decay. Offline-safe; no server, no LLM key needed.

from datetime import datetime, timedelta


def test_bypass_policy_blocks_security():
    from services.taxonomy import apply_bypass_policy
    assert apply_bypass_policy(["security", "tools"]) == ["tools"]
    assert apply_bypass_policy([]) == []
    assert apply_bypass_policy(None) == []


def test_score_baseline_carries_policy_fields_and_v1_keys():
    from services.baseline_v2 import score_baseline
    from services.diagnostic import evaluate_diagnostic
    # sec_1's real bank answer: perfect score on security must still not bypass it
    answers = {"sec_1": "Every 90 days"}
    v1 = evaluate_diagnostic(answers, role="Software Engineer")
    v2 = score_baseline(answers, role="Software Engineer")
    for k in ["bypassed_topics", "correct_count", "total_questions",
              "score_percentage", "xp_to_award"]:
        assert v2[k] == v1[k], k
    assert "bypass_eligible" in v2 and "must_complete" in v2
    assert "security" not in v2["bypass_eligible"]
    assert "security" in v2["must_complete"]
    assert v2["calibration"] == {"applied": False, "adjustments": {}}


def test_graded_eval_unseen_only_and_stripped():
    from services.quiz_generator import build_graded_eval, grade_graded_eval
    from services.eval_seen import qhash
    from services.quiz_generator import _full_static_bank

    bank_qs = [i["question"] for i in _full_static_bank("security")]
    seen = {qhash(bank_qs[0]), qhash(bank_qs[1])}
    built = build_graded_eval("Backend Engineer", seen, count=20, seed=1)
    assert built["complete"] is True and built["count"] == 20
    got = [q["question"] for q in built["questions"]]
    assert bank_qs[0] not in got and bank_qs[1] not in got
    assert all("correct_answer" not in q and "evidence_quote" not in q for q in built["questions"])
    assert all("eval_id" in q and ":" in q["eval_id"] for q in built["questions"])

    # grade honestly: answer everything from the bank key
    by_id = {}
    for t in ("company_basics", "security", "tools", "git_workflow",
              "architecture", "deployment"):
        for idx, item in enumerate(_full_static_bank(t)):
            by_id[f"{t}:{idx}"] = item["correct_answer"]
    answers = {q["eval_id"]: by_id[q["eval_id"]] for q in built["questions"]}
    res = grade_graded_eval(answers, role="Backend Engineer")
    assert res["score_percentage"] == 100
    assert res["certified"] is True

    wrong = dict(answers)
    sec = next(q["eval_id"] for q in built["questions"] if q["topic"] == "security")
    wrong[sec] = "definitely not the answer"
    res2 = grade_graded_eval(wrong, role="Backend Engineer")
    assert res2["certified"] is False  # compliance miss blocks certification


def test_effective_mastery_decay():
    from services.quiz_policy_v2 import effective_mastery
    now = datetime.utcnow()
    assert effective_mastery(90, now) == 90
    assert effective_mastery(90, now - timedelta(days=7)) == 90  # grace
    assert effective_mastery(90, now - timedelta(days=12)) == 80  # 5 days x 2
    assert effective_mastery(10, now - timedelta(days=100)) == 0  # floor
    assert effective_mastery(90, None) == 90


def test_seen_tracking_roundtrip(tmp_path):
    import services.eval_seen as es
    es.SEEN_DB = str(tmp_path / "seen.db")
    try:
        assert es.log_seen("u1", ["What is X?", "What is Y?"]) == 2
        assert es.log_seen("u1", ["What is X?"]) == 0  # idempotent
        assert es.qhash("What is X?") in es.get_seen_hashes("u1")
        assert es.get_seen_hashes("nobody") == set()
    finally:
        es.SEEN_DB = "./onboardiq.db"
