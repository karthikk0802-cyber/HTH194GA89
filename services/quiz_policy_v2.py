# Quiz policy v2 sidecar — reads adaptive thresholds, never edits adaptive.py.
# Personalization = weakness-weighted topic pick + auto difficulty.
# Quiz content itself always comes from v1 generate_quiz_for_topic (shape unchanged).

import random


def pick_difficulty(mastery_score: int) -> str:
    """Mirror adaptive.py tiers read-only: <40 Beginner, <70 Intermediate, else Expert."""
    try:
        m = int(mastery_score)
    except (TypeError, ValueError):
        m = 0
    if m >= 80:
        return "Expert"
    if m >= 50:
        return "Intermediate"
    return "Beginner"


DECAY_POINTS_PER_DAY = 2
DECAY_GRACE_DAYS = 7


def effective_mastery(mastery_score: int, last_attempt_at, now=None) -> int:
    """Forgetting curve for v2 targeting: stored scores never change, but
    targeting discounts stale mastery (2 pts/day after a 7-day grace).
    v1 display paths are untouched."""
    from datetime import datetime
    try:
        m = int(mastery_score)
    except (TypeError, ValueError):
        return 0
    if last_attempt_at is None:
        return m
    now = now or datetime.utcnow()
    try:
        days = (now - last_attempt_at).days
    except TypeError:
        return m
    overdue = max(0, days - DECAY_GRACE_DAYS)
    return max(0, m - overdue * DECAY_POINTS_PER_DAY)


def pick_next_topic(weak_topics, states=None, required_topics=None, seed=None) -> dict:
    """70% weakest / 30% review-or-next. Returns {topic_id, reason} only."""
    rng = random.Random(seed)
    weak = [t for t in (weak_topics or []) if t]
    if weak and rng.random() < 0.7:
        topic = rng.choice(weak)
        return {"topic_id": topic, "reason": f"Targeting weakness: {topic}"}
    pool = [t for t in (required_topics or []) if t not in weak] or list(required_topics or []) or weak
    if not pool:
        return {"topic_id": "", "reason": "No topics available"}
    topic = rng.choice(pool)
    return {"topic_id": topic, "reason": f"Review/rotation: {topic}"}


def generate_personalized_quiz(topic: str, role: str = "all", mastery_score: int = 0):
    """Resolve difficulty from mastery, call v1 generator, add reason only."""
    from services.quiz_generator import generate_quiz_for_topic

    difficulty = pick_difficulty(mastery_score)
    quiz = generate_quiz_for_topic(topic, role=role, difficulty=difficulty)
    if isinstance(quiz, dict):
        quiz = dict(quiz)
        quiz.setdefault("difficulty", difficulty)
        quiz["personalization"] = {
            "reason": f"mastery {mastery_score} -> {difficulty} for {topic}",
            "target_difficulty": difficulty,
        }
    return quiz
