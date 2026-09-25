# Baseline v2 sidecar — wraps v1 diagnostic, never edits it.
# v1 shapes are returned verbatim; v2 only ADDS topic_scores/weak/strong.

from services.diagnostic import evaluate_diagnostic, get_diagnostic_questions_for_role
from services.taxonomy import get_role_card


def get_baseline_questions(role: str, per_topic: int = 3, profile=None):
    """Role-card baseline: per_topic general questions per required topic.

    Returns v1 item shape + additive phase/required_depth.
    Optional profile (resume calibration): claimed topics get +1 question
    (capped by the card's baseline_count) and a raised required_depth floor.
    profile=None -> today's behavior, byte-identical.
    """
    from services.resume_profile import map_to_role_card

    card = get_role_card(role)
    topics = card["topics"]
    adjustments = {}
    if isinstance(profile, dict):
        if isinstance(profile.get("topic_adjustments"), dict):
            adjustments = profile["topic_adjustments"]
        else:
            adjustments = map_to_role_card(profile, role)
    depth_order = ["Beginner", "Intermediate", "Expert"]
    total = 0
    want_map = {}
    for t, spec in topics.items():
        want = min(per_topic, spec.get("baseline_count", per_topic))
        if t in adjustments:
            want = min(spec.get("baseline_count", per_topic), want + adjustments[t].get("extra_questions", 0))
        want_map[t] = want
        total += want

    # Pull a generous v1 pool once, then slice per topic (one LLM-free call path).
    pool = get_diagnostic_questions_for_role(role=role, count=max(total, 10))
    by_topic: dict[str, list] = {}
    for q in pool:
        by_topic.setdefault(q.get("topic", ""), []).append(q)

    out = []
    for topic, spec in topics.items():
        want = want_map[topic]
        # Prefer on-topic questions, backfill from pool if bank is thin.
        picks = list(by_topic.get(topic, []))[:want]
        if len(picks) < want:
            for q in pool:
                if q not in picks and q not in out:
                    picks.append(q)
                if len(picks) >= want:
                    break
        depth = spec.get("depth", "Beginner")
        if topic in adjustments:
            floor = adjustments[topic].get("start_difficulty", depth)
            if depth_order.index(floor) > depth_order.index(depth):
                depth = floor
        for q in picks[:want]:
            item = dict(q)
            item["phase"] = "baseline"
            item["required_depth"] = depth
            out.append(item)
    return out


def score_baseline(answers: dict, role: str = "Software Engineer", profile=None):
    """Score baseline via v1, then add per-topic strength profile.

    Returns ALL v1 keys with identical values + topic_scores/weak_topics/strong_topics.
    strength: pct>=80 strong, >=50 ok, else weak.
    Optional profile adds additive calibration:{applied, adjustments} (default off).
    """
    v1 = evaluate_diagnostic(answers, role=role)
    evals = v1.get("evaluations", [])

    per_topic: dict[str, dict] = {}
    for ev in evals:
        t = ev.get("topic", "unknown")
        d = per_topic.setdefault(t, {"correct": 0, "total": 0})
        d["total"] += 1
        if ev.get("is_correct"):
            d["correct"] += 1

    topic_scores = {}
    weak_topics: list[str] = []
    strong_topics: list[str] = []
    for t, d in per_topic.items():
        pct = int(d["correct"] * 100 / d["total"]) if d["total"] else 0
        strength = "strong" if pct >= 80 else ("ok" if pct >= 50 else "weak")
        topic_scores[t] = {**d, "pct": pct, "strength": strength}
        if strength == "weak":
            weak_topics.append(t)
        elif strength == "strong":
            strong_topics.append(t)

    # Compliance policy: evaluated bypasses, not raw scores, drive progression.
    from services.taxonomy import apply_bypass_policy, NON_BYPASSABLE_TOPICS
    policy_bypassed = apply_bypass_policy(strong_topics)
    blocked = [t for t in strong_topics if t in NON_BYPASSABLE_TOPICS]

    calibration = {"applied": False, "adjustments": {}}
    if isinstance(profile, dict):
        adj = profile.get("topic_adjustments", {})
        calibration = {"applied": True, "adjustments": adj if isinstance(adj, dict) else {}}

    return {
        **v1,
        "topic_scores": topic_scores,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "bypass_eligible": policy_bypassed,
        "must_complete": blocked,
        "role_card": role,
        "calibration": calibration,
    }
