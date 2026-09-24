import pytest
import json
from datetime import datetime, timedelta
from services.document_processor import chunk_text, extract_metadata_from_text, extract_text
from services.roles import ROLES, TOPICS, get_role_topics
from services.adaptive import build_competency_graph, update_topic_state, rank_next_topics, SPACED_INTERVALS
from services.diagnostic import DIAGNOSTIC_QUESTIONS, evaluate_diagnostic
from services.readiness import compute_readiness, generate_readiness_report_md
from services.gamification import award_xp, check_streak, update_badges
from services.resources import get_resources_for_topic, CURATED_RESOURCES
from services.voice import handle_voice_interaction
from services.rag import determine_evidence_confidence
from services.scenarios import SCENARIOS
from services.db import DocumentModel, QuizFeedbackModel, UserTopicState, UserProfileModel

# Mock State for testing
class MockState:
    def __init__(self, t_id, mastery=0, diff="Beginner", status="Locked"):
        self.topic_id = t_id
        self.mastery_score = mastery
        self.difficulty = diff
        self.status = status
        self.last_attempt_at = None
        self.next_review_at = None
        self.review_interval_days = 1

# Mock Profile for testing
class MockProfile:
    def __init__(self, user_id="test_user", xp=0, level=1, streak_days=0, badges="[]", last_login=None):
        self.user_id = user_id
        self.xp = xp
        self.level = level
        self.streak_days = streak_days
        self.badges = badges
        self.last_login = last_login

# -------------------------------------------------------------
# 1. Document Processor Tests
# -------------------------------------------------------------
def test_chunking_logic():
    text = "Para 1\n\nPara 2\n\nPara 3"
    chunks = chunk_text(text, chunk_size=10, overlap=5)
    assert len(chunks) > 1
    assert "Para 1" in chunks[0]

def test_chunking_single_paragraph():
    text = "Single paragraph without breaks."
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) == 1
    assert chunks[0] == "Single paragraph without breaks."

def test_extract_text_txt():
    sample_bytes = b"Hello, Nexora onboarding!"
    text = extract_text(sample_bytes, "welcome.txt")
    assert text == "Hello, Nexora onboarding!"

def test_metadata_extraction():
    text = "Title: Engineering Standard\nRole: engineering\n\nWe do trunk based dev."
    meta = extract_metadata_from_text(text)
    assert meta["title"] == "Engineering Standard"
    assert meta["role"] == "engineering"

def test_metadata_extraction_defaults():
    text = "No explicit title or role line here."
    meta = extract_metadata_from_text(text, default_role="general")
    assert meta["title"] == "Unknown Document"
    assert meta["role"] == "general"

# -------------------------------------------------------------
# 2. Roles & Topic Dependency Graph Tests
# -------------------------------------------------------------
def test_roles_and_topics():
    assert "Software Engineer" in ROLES
    assert "company_basics" in TOPICS
    se_topics = get_role_topics("Software Engineer")
    assert "company_basics" in se_topics
    assert "security" in se_topics
    assert "tools" in se_topics
    assert "git_workflow" in se_topics
    assert "architecture" in se_topics

def test_competency_graph_edges():
    G = build_competency_graph()
    assert G.has_edge("company_basics", "security")
    assert G.has_edge("tools", "git_workflow")
    assert G.has_edge("git_workflow", "architecture")

def test_rank_next_topics_review_due():
    now = datetime.utcnow()
    state_rev = MockState("company_basics", mastery=90, diff="Expert", status="Completed")
    state_rev.next_review_at = now - timedelta(hours=1)
    
    ranked = rank_next_topics([state_rev], ["company_basics", "security"])
    assert len(ranked) > 0
    assert ranked[0]["topic_id"] == "company_basics"
    assert ranked[0]["score"] == 100

def test_rank_next_topics_prereqs_unlocked():
    s1 = MockState("company_basics", mastery=85, diff="Expert", status="Completed")
    s2 = MockState("tools", mastery=85, diff="Expert", status="Completed")
    s3 = MockState("git_workflow", mastery=0, diff="Beginner", status="Locked")
    
    ranked = rank_next_topics([s1, s2, s3], ["company_basics", "tools", "git_workflow"])
    git_ranked = next((r for r in ranked if r["topic_id"] == "git_workflow"), None)
    assert git_ranked is not None
    assert git_ranked["status"] == "Recommended"

# -------------------------------------------------------------
# 3. Adaptive Difficulty & Spaced Repetition Tests
# -------------------------------------------------------------
def test_adaptive_difficulty_progression():
    state = MockState("test", mastery=65, diff="Intermediate", status="Current")
    # Simulate correct answer (+10 for intermediate)
    updated = update_topic_state(state, is_correct=True)
    assert updated.mastery_score == 75
    assert updated.difficulty == "Intermediate"
    
    # Another correct pushes over 80
    updated = update_topic_state(updated, is_correct=True)
    assert updated.mastery_score >= 80
    assert updated.difficulty == "Expert"
    assert updated.status == "Completed"
    assert updated.next_review_at is not None

def test_adaptive_incorrect_answer_regression():
    state = MockState("test", mastery=45, diff="Intermediate", status="Current")
    # Incorrect answer (-15)
    updated = update_topic_state(state, is_correct=False)
    assert updated.mastery_score == 30
    assert updated.difficulty == "Beginner"

def test_adaptive_spaced_repetition_intervals():
    state = MockState("test", mastery=75, diff="Intermediate", status="Current")
    state.review_interval_days = 1
    updated = update_topic_state(state, is_correct=True)
    assert updated.status == "Completed"
    assert updated.review_interval_days == 3  # Advanced to next interval in [1, 3, 7, 14, 30]

# -------------------------------------------------------------
# 4. Diagnostic Pre-Assessment Tests
# -------------------------------------------------------------
def test_diagnostic_evaluation():
    perfect_answers = {q["id"]: q["answer"] for q in DIAGNOSTIC_QUESTIONS}
    bypassed = evaluate_diagnostic(perfect_answers)
    assert "company_basics" in bypassed
    assert "security" in bypassed
    assert "tools" in bypassed
    assert "git_workflow" in bypassed

def test_diagnostic_partial_answers():
    # Only answer company_basics correctly
    partial_answers = {
        "q1": "10 AM to 3 PM EST",
        "q6": "$50/month"
    }
    bypassed = evaluate_diagnostic(partial_answers)
    assert "company_basics" in bypassed
    assert "security" not in bypassed

# -------------------------------------------------------------
# 5. Readiness Evaluation Tests
# -------------------------------------------------------------
def test_readiness_evaluation():
    req_topics = ["t1", "t2"]
    
    # Not Ready Case
    states = [MockState("t1", mastery=85), MockState("t2", mastery=10)]
    res = compute_readiness(states, req_topics)
    assert res["status"] == "NOT YET READY"
    assert "t2" in res["missing"]
    
    # Ready With Gaps Case
    states2 = [MockState("t1", mastery=60), MockState("t2", mastery=60)]
    res2 = compute_readiness(states2, req_topics)
    assert res2["status"] == "READY WITH GAPS"
    
    # Fully Ready Case (100% intermediate+, >=50% Expert+)
    states3 = [MockState("t1", mastery=85), MockState("t2", mastery=60)]
    res3 = compute_readiness(states3, req_topics)
    assert res3["status"] == "READY"

def test_readiness_report_markdown():
    profile = MockProfile(user_id="john_doe")
    states = [MockState("security", mastery=85, diff="Expert")]
    readiness = {"status": "READY", "score": 85, "missing": []}
    report = generate_readiness_report_md(profile, readiness, states, "Software Engineer")
    assert "john_doe" in report
    assert "READY" in report
    assert "security" in report
    assert "85/100" in report

# -------------------------------------------------------------
# 6. Gamification System Tests
# -------------------------------------------------------------
def test_gamification_xp_and_levels():
    profile = MockProfile(xp=90, level=1)
    gained = award_xp(profile, "quiz_correct")
    assert gained == 15
    assert profile.xp == 105
    assert profile.level == 2  # Leveled up past 100 XP

def test_gamification_streak_continuation():
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    profile = MockProfile(streak_days=3, last_login=yesterday)
    check_streak(profile)
    assert profile.streak_days == 4

def test_gamification_streak_reset():
    now = datetime.utcnow()
    old_date = now - timedelta(days=3)
    profile = MockProfile(streak_days=5, last_login=old_date)
    check_streak(profile)
    assert profile.streak_days == 1

def test_gamification_badges():
    profile = MockProfile(badges="[]", streak_days=7)
    states = [MockState("t1", diff="Expert")] * 5
    new_badges = update_badges(profile, states)
    assert "First Mastery" in new_badges
    assert "Scholar" in new_badges
    assert "Week Warrior" in new_badges

# -------------------------------------------------------------
# 7. Resources, Voice, & RAG Confidence Tests
# -------------------------------------------------------------
def test_curated_resources():
    sec_res = get_resources_for_topic("security")
    assert len(sec_res) > 0
    assert any("OWASP" in r["title"] for r in sec_res)
    assert get_resources_for_topic("non_existent") == []

def test_voice_graceful_degradation():
    empty_res = handle_voice_interaction("", "explain")
    assert "Gracefully falling back to text mode" in empty_res
    
    valid_res = handle_voice_interaction("What is GitFlow?", "explain")
    assert "Voice Tutor (EXPLAIN MODE)" in valid_res
    assert "What is GitFlow?" in valid_res

def test_rag_evidence_confidence_scoring():
    # Strong (< 0.3)
    res_strong = {"documents": [["doc1"]], "distances": [[0.15, 0.22]]}
    assert determine_evidence_confidence(res_strong) == "Strong"
    
    # Moderate (< 0.5)
    res_mod = {"documents": [["doc1"]], "distances": [[0.35, 0.42]]}
    assert determine_evidence_confidence(res_mod) == "Moderate"
    
    # Limited (< 0.7)
    res_lim = {"documents": [["doc1"]], "distances": [[0.55, 0.65]]}
    assert determine_evidence_confidence(res_lim) == "Limited"
    
    # Insufficient (>= 0.7 or empty)
    res_ins = {"documents": [["doc1"]], "distances": [[0.85, 0.90]]}
    assert determine_evidence_confidence(res_ins) == "Insufficient"
    assert determine_evidence_confidence(None) == "Insufficient"

def test_scenarios_structure():
    assert "security" in SCENARIOS
    assert "git_workflow" in SCENARIOS
    assert "title" in SCENARIOS["security"]
    assert "text" in SCENARIOS["security"]

# -------------------------------------------------------------
# 8. Separate Auth Database & Password Hashing Tests
# -------------------------------------------------------------
def test_auth_password_hashing_and_verification():
    from services.auth_db import hash_password, verify_password, AuthSessionLocal, UserAuthModel
    hashed = hash_password("secret_password_123")
    assert hashed != "secret_password_123"
    assert verify_password("secret_password_123", hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_auth_database_isolation():
    from services.auth_db import AuthSessionLocal, UserAuthModel
    adb = AuthSessionLocal()
    try:
        users_count = adb.query(UserAuthModel).count()
        assert users_count >= 1
    finally:
        adb.close()
