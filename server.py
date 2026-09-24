import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Import Database & Services
from services.auth_db import (
    get_auth_db, UserAuthModel, hash_password, verify_password, seed_default_auth_users, AuthSessionLocal
)
from services.db import (
    get_db, DocumentModel, QuizFeedbackModel, UserTopicState, UserProfileModel, SessionLocal, SignoffModel
)
from services.roles import ROLES, TOPICS, get_role_topics
from services.diagnostic import (
    DIAGNOSTIC_QUESTIONS, evaluate_diagnostic, get_diagnostic_questions_for_role, is_answer_match
)
from services.adaptive import build_competency_graph, update_topic_state, rank_next_topics


from services.readiness import compute_readiness, generate_readiness_report_md
from services.gamification import award_xp, check_streak, update_badges
from services.resources import CURATED_RESOURCES, get_resources_for_topic
from services.voice import handle_voice_interaction
from services.rag import generate_rag_response
from services.quiz_generator import generate_quiz_for_topic
from services.quiz_validator import validate_quiz_question
from services.teaching import generate_remediation, generate_explain_again
from services.scenarios import SCENARIOS, evaluate_scenario_response
from services.document_processor import extract_text, chunk_text, extract_metadata_from_text
from services.embedding import add_chunks_to_chroma, delete_document_from_chroma
from services.admin_auth import (
    ensure_admin_seed,
    is_admin_token,
    require_admin,
)
from services.taxonomy import DEPARTMENTS, ROLE_CARDS, get_role_card, apply_bypass_policy
from services.baseline_v2 import get_baseline_questions, score_baseline
from services.quiz_policy_v2 import (
    generate_personalized_quiz,
    pick_difficulty,
    pick_next_topic,
    effective_mastery,
)

ensure_admin_seed()

# First-login default password for admin-created users (env-overridable).
DEFAULT_EMPLOYEE_PASSWORD = os.getenv("DEFAULT_EMPLOYEE_PASSWORD", "employee@123")

def _admin_guard(authorization: Optional[str] = Header(default=None)) -> str:
    """Header-injecting wrapper so Depends gets the Authorization header."""
    return require_admin(authorization)

app = FastAPI(
    title="OnboardIQ API Server",
    description="Backend REST API for OnboardIQ Adaptive Corporate Onboarding Platform",
    version="2.0.0"
)

# Enable CORS for React frontend (Vite default port 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic Request/Response Models
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: Optional[str] = "Software Engineer"
    department: Optional[str] = "Engineering"

class LoginRequest(BaseModel):
    username: str
    password: str

class DiagnosticSubmitRequest(BaseModel):
    userId: str
    role: str
    answers: Dict[str, str]

class QARequest(BaseModel):
    query: str
    role: Optional[str] = "all"

class QuizSubmitRequest(BaseModel):
    userId: str
    topicId: str
    selectedAnswer: str
    correctAnswer: str

class RemediationRequest(BaseModel):
    question: str
    userAnswer: str
    correctAnswer: str
    evidenceQuote: Optional[str] = ""

class ExplainAgainRequest(BaseModel):
    question: str
    userAnswer: str
    correctAnswer: str
    previousExplanation: str

class QuizFeedbackRequest(BaseModel):
    questionText: str
    reason: str
    comments: Optional[str] = ""

class ScenarioEvaluateRequest(BaseModel):
    userId: str
    scenarioId: str
    userResponse: str

class VoiceInteractionRequest(BaseModel):
    transcript: str
    mode: Optional[str] = "explain"

# ---------------------------------------------------------------------------
# 1. Authentication Endpoints (Dedicated auth.db)
# ---------------------------------------------------------------------------
@app.post("/api/auth/register")
def register_user(req: RegisterRequest, authorization: Optional[str] = Header(default=None)):
    # Public self-registration disabled — admin-only user creation.
    if not is_admin_token(authorization):
        raise HTTPException(status_code=403, detail="Self-registration disabled — contact admin")
    db = AuthSessionLocal()
    try:
        existing = db.query(UserAuthModel).filter(
            (UserAuthModel.username == req.username) | (UserAuthModel.email == req.email)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username or Email already exists")
        
        new_user = UserAuthModel(
            username=req.username,
            email=req.email,
            password_hash=hash_password(req.password),
            full_name=req.full_name,
            role=req.role or "Software Engineer",
            department=req.department or "Engineering",
            is_admin=(req.role in ["Admin", "Manager"])
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Also ensure UserProfileModel exists in onboardiq.db
        odb = SessionLocal()
        try:
            profile = odb.query(UserProfileModel).filter(UserProfileModel.user_id == new_user.username).first()
            if not profile:
                profile = UserProfileModel(user_id=new_user.username, xp=0, level=1, streak_days=1)
                odb.add(profile)
                odb.commit()
        finally:
            odb.close()

        return {
            "success": True,
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role,
                "department": new_user.department,
                "is_admin": new_user.is_admin
            },
            "token": f"token_{new_user.username}_{new_user.id}"
        }
    finally:
        db.close()

@app.post("/api/auth/login")
def login_user(req: LoginRequest):
    db = AuthSessionLocal()
    try:
        user = db.query(UserAuthModel).filter(
            (UserAuthModel.username == req.username) | (UserAuthModel.email == req.username)
        ).first()
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Update streak & login stats
        odb = SessionLocal()
        try:
            profile = odb.query(UserProfileModel).filter(UserProfileModel.user_id == user.username).first()
            if not profile:
                profile = UserProfileModel(user_id=user.username, xp=0, level=1, streak_days=1)
                odb.add(profile)
            else:
                check_streak(profile)
            odb.commit()
        finally:
            odb.close()

        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "department": user.department,
                "is_admin": user.is_admin,
                "must_change_password": user.password_hash == hash_password(DEFAULT_EMPLOYEE_PASSWORD)
            },
            "token": f"token_{user.username}_{user.id}"
        }
    finally:
        db.close()

@app.get("/api/auth/users")
def get_auth_users(authorization: Optional[str] = Header(default=None)):
    """List all accounts — admin-only (used by admin portal + gated demo switch)."""
    if not is_admin_token(authorization):
        raise HTTPException(status_code=403, detail="Admin access required")
    db = AuthSessionLocal()
    try:
        users = db.query(UserAuthModel).all()
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "department": u.department,
                "is_admin": u.is_admin
            }
            for u in users
        ]
    finally:
        db.close()

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

@app.post("/api/auth/change-password")
def change_password(req: ChangePasswordRequest):
    if not req.new_password or len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    if req.new_password == req.old_password:
        raise HTTPException(status_code=400, detail="New password must differ from the old password")
    db = AuthSessionLocal()
    try:
        user = db.query(UserAuthModel).filter(UserAuthModel.username == req.username).first()
        if not user or not verify_password(req.old_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        user.password_hash = hash_password(req.new_password)
        db.commit()
        return {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "department": user.department,
                "is_admin": user.is_admin,
                "must_change_password": False
            }
        }
    finally:
        db.close()

@app.get("/api/auth/me")
def get_current_user_profile(userId: str):
    db = AuthSessionLocal()
    try:
        user = db.query(UserAuthModel).filter(UserAuthModel.username == userId).first()
        if not user:
            return {
                "username": userId,
                "full_name": userId.replace("_", " ").title(),
                "role": "Software Engineer",
                "department": "Engineering",
                "is_admin": False
            }
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "is_admin": user.is_admin
        }
    finally:
        db.close()

# ---------------------------------------------------------------------------
# 2. Roles & Diagnostic Pre-Assessment Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/roles")
def list_roles():
    return {
        "roles": ROLES,
        "topics": TOPICS
    }

@app.get("/api/roles/{role_name}/topics")
def get_topics_for_role(role_name: str):
    return get_role_topics(role_name)

@app.get("/api/diagnostic/questions")
def get_diagnostic_questions(role: Optional[str] = "Software Engineer", count: Optional[int] = 10):
    return get_diagnostic_questions_for_role(role=role or "Software Engineer", count=count or 10)

@app.post("/api/diagnostic/evaluate")
def submit_diagnostic(req: DiagnosticSubmitRequest):
    eval_data = evaluate_diagnostic(req.answers, role=req.role)
    bypassed = apply_bypass_policy(eval_data["bypassed_topics"])
    role_topics = get_role_topics(req.role)
    
    # Update topic states in DB
    db = SessionLocal()
    xp_gained = 0
    profile_xp = 0
    profile_level = 1
    try:
        for topic_id in role_topics:
            state = db.query(UserTopicState).filter(
                UserTopicState.user_id == req.userId,
                UserTopicState.topic_id == topic_id
            ).first()
            if not state:
                state = UserTopicState(user_id=req.userId, topic_id=topic_id)
                db.add(state)
                
            if topic_id in bypassed:
                state.status = "Completed"
                state.difficulty = "Expert"
                state.mastery_score = 90
                state.last_attempt_at = datetime.utcnow()
                state.next_review_at = datetime.utcnow() + timedelta(days=7)
            else:
                if state.status == "Locked":
                    # If prerequisite met or base topic, unlock
                    prereqs = TOPICS.get(topic_id, {}).get("prerequisites", [])
                    if not prereqs or all(p in bypassed for p in prereqs):
                        state.status = "Current"
                        state.difficulty = "Beginner"
        
        # Award XP for completing diagnostic based on score/marks
        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == req.userId).first()
        if not profile:
            profile = UserProfileModel(user_id=req.userId, xp=0, level=1, streak_days=1)
            db.add(profile)
            
        # XP is engagement fuel, not a measure: award diagnostic XP on first
        # completion only, so retakes can't farm it. States/scores still update.
        prior_attempt = db.query(UserTopicState).filter(
            UserTopicState.user_id == req.userId,
            UserTopicState.last_attempt_at.isnot(None)
        ).first()
        xp_to_add = eval_data.get("xp_to_award", (eval_data.get("correct_count", 0) * 10) + 50)
        if prior_attempt is not None:
            xp_to_add = 0
        xp_gained = award_xp(profile, "preassessment_completed", score=xp_to_add)
        profile_xp = profile.xp
        profile_level = profile.level
        
        all_states = db.query(UserTopicState).filter(UserTopicState.user_id == req.userId).all()
        update_badges(profile, all_states)
        
        db.commit()
    finally:
        db.close()
        
    return {
        "success": True,
        "bypassed_topics": [t for t in bypassed if t in role_topics],
        "bypassed_titles": [role_topics[t]["title"] for t in bypassed if t in role_topics],
        "correct_count": eval_data.get("correct_count", 0),
        "total_questions": eval_data.get("total_questions", len(req.answers)),
        "score_percentage": eval_data.get("score_percentage", 0),
        "xp_gained": xp_gained,
        "total_xp": profile_xp,
        "level": profile_level,
        "evaluations": eval_data.get("evaluations", [])
    }


# ---------------------------------------------------------------------------
# 3. Adaptive Learning Path & Competency Graph Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/learning-path/{userId}")
def get_user_learning_path(userId: str, role: Optional[str] = "Software Engineer"):
    db = SessionLocal()
    try:
        role_topics = get_role_topics(role)
        states = db.query(UserTopicState).filter(UserTopicState.user_id == userId).all()
        
        # Initialize default states if not created yet
        if not states:
            for i, t_id in enumerate(role_topics):
                new_state = UserTopicState(
                    user_id=userId,
                    topic_id=t_id,
                    status="Current" if i == 0 else "Locked",
                    difficulty="Beginner",
                    mastery_score=0
                )
                db.add(new_state)
            db.commit()
            states = db.query(UserTopicState).filter(UserTopicState.user_id == userId).all()
            
        ranked = rank_next_topics(states, list(role_topics.keys()))
        state_map = {s.topic_id: s for s in states}
        
        competencies = []
        for t_id, t_data in role_topics.items():
            s = state_map.get(t_id)
            competencies.append({
                "topic_id": t_id,
                "title": t_data["title"],
                "prerequisites": [TOPICS[p]["title"] for p in t_data["prerequisites"] if p in TOPICS],
                "status": s.status if s else "Locked",
                "difficulty": s.difficulty if s else "Beginner",
                "mastery_score": s.mastery_score if s else 0,
                "next_review_at": s.next_review_at.isoformat() if s and s.next_review_at else None
            })
            
        # Graph structure
        G = build_competency_graph()
        edges = [{"source": u, "target": v, "source_title": TOPICS.get(u, {}).get("title", u), "target_title": TOPICS.get(v, {}).get("title", v)} for u, v in G.edges() if u in role_topics and v in role_topics]
        
        return {
            "role": role,
            "ranked_topics": ranked,
            "today_focus": ranked[0] if ranked else None,
            "competencies": competencies,
            "graph_edges": edges
        }
    finally:
        db.close()

# ---------------------------------------------------------------------------
# 4. Grounded RAG Knowledge Coach Q&A
# ---------------------------------------------------------------------------
@app.post("/api/qa/ask")
def ask_knowledge_coach(req: QARequest):
    trace = generate_rag_response(req.query, role=req.role or "all")
    return trace

# ---------------------------------------------------------------------------
# 5. Interactive Grounded Quizzes & Remediation
# ---------------------------------------------------------------------------
@app.get("/api/quiz/generate")
def get_quiz_question(topic: str, role: Optional[str] = "all", difficulty: Optional[str] = "Beginner"):
    quiz = generate_quiz_for_topic(topic, role=role, difficulty=difficulty)
    if "error" in quiz:
        # Fallback to topic-specific standard quiz
        return {
            "question": f"What is the standard Nexora operating policy regarding {topic}?",
            "options": [
                f"Adhere strictly to official {topic} guidelines",
                "Operate without approval or review",
                "Use external unauthorized third-party tooling",
                "Bypass security and audit controls"
            ],
            "correct_answer": f"Adhere strictly to official {topic} guidelines",
            "learning_objective": f"Mastery of {topic} compliance and workflows",
            "evidence_quote": f"Employees must follow approved standards for {topic}.",
            "citations": [f"{topic} Policy"]
        }
    
    # Validate question through anti-hallucination gate
    is_valid = validate_quiz_question(quiz, quiz.get("evidence_quote", ""))
    quiz["validation_passed"] = is_valid
    return quiz

@app.get("/api/quiz/session")
def get_quiz_session(topic: str, role: Optional[str] = "all", difficulty: Optional[str] = "Beginner", count: Optional[int] = 20, userId: Optional[str] = None):
    """20-question no-repeat session. Single-question /api/quiz/generate untouched."""
    from services.quiz_generator import generate_quiz_session
    session = generate_quiz_session(topic, role=role or "all", difficulty=difficulty or "Beginner", count=count or 20)
    for q in session["questions"]:
        q["validation_passed"] = validate_quiz_question(q, q.get("evidence_quote", ""))
    if userId:
        try:
            from services.eval_seen import log_seen
            log_seen(userId, [q.get("question", "") for q in session["questions"]])
        except Exception:
            pass
    return session

@app.post("/api/quiz/submit")
def submit_quiz_answer(req: QuizSubmitRequest):
    is_correct = is_answer_match(req.selectedAnswer, req.correctAnswer)
    db = SessionLocal()
    try:
        state = db.query(UserTopicState).filter(
            UserTopicState.user_id == req.userId,
            UserTopicState.topic_id == req.topicId
        ).first()
        if not state:
            state = UserTopicState(user_id=req.userId, topic_id=req.topicId, status="Current", difficulty="Beginner", mastery_score=0)
            db.add(state)
            
        updated_state = update_topic_state(state, is_correct=is_correct)
        
        # Update user profile and award XP
        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == req.userId).first()
        xp_gained = 0
        new_badges = []
        if profile:
            if is_correct:
                xp_gained = award_xp(profile, "quiz_correct")
            all_states = db.query(UserTopicState).filter(UserTopicState.user_id == req.userId).all()
            new_badges = update_badges(profile, all_states)
            
        db.commit()
        
        return {
            "is_correct": is_correct,
            "mastery_score": updated_state.mastery_score,
            "difficulty": updated_state.difficulty,
            "status": updated_state.status,
            "xp_gained": xp_gained,
            "new_badges": new_badges
        }
    finally:
        db.close()

@app.post("/api/quiz/remediation")
def get_quiz_remediation(req: RemediationRequest):
    rem = generate_remediation(req.question, req.userAnswer, req.correctAnswer, req.evidenceQuote)
    return rem

@app.post("/api/quiz/explain-again")
def get_quiz_explain_again(req: ExplainAgainRequest):
    explanation = generate_explain_again(req.question, req.userAnswer, req.correctAnswer, req.previousExplanation)
    return {"explanation": explanation}

@app.post("/api/quiz/feedback")
def submit_quiz_feedback(req: QuizFeedbackRequest):
    db = SessionLocal()
    try:
        fb = QuizFeedbackModel(
            question_text=req.questionText,
            reason=req.reason,
            feedback_text=req.comments or ""
        )
        db.add(fb)
        db.commit()
        return {"success": True, "message": "Feedback submitted successfully for administrative review."}
    finally:
        db.close()

# ---------------------------------------------------------------------------
# 6. Applied Scenarios & Voice Tutor Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/scenarios")
def get_scenarios():
    return [
        {"id": k, "title": v["title"], "text": v["text"], "topic_id": v["topic_id"]}
        for k, v in SCENARIOS.items()
    ]

@app.post("/api/scenarios/evaluate")
def evaluate_scenario(req: ScenarioEvaluateRequest):
    scenario = SCENARIOS.get(req.scenarioId)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    eval_result = evaluate_scenario_response(scenario["text"], req.userResponse, topic_id=scenario.get("topic_id", "security"))
    
    # Award XP & update state
    db = SessionLocal()
    try:
        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == req.userId).first()
        xp_gained = 0
        if profile:
            score = eval_result.get("mastery_impact", 50)
            xp_gained = award_xp(profile, "scenario_completed", score=score)
            
        state = db.query(UserTopicState).filter(
            UserTopicState.user_id == req.userId,
            UserTopicState.topic_id == scenario["topic_id"]
        ).first()
        if state:
            state.mastery_score = min(100, state.mastery_score + eval_result.get("mastery_impact", 10))
            if state.mastery_score >= 80:
                state.difficulty = "Expert"
                state.status = "Completed"
        db.commit()
    finally:
        db.close()
        
    eval_result["xp_gained"] = xp_gained
    return eval_result


@app.post("/api/voice/interact")
def voice_tutor_interaction(req: VoiceInteractionRequest):
    reply = handle_voice_interaction(req.transcript, req.mode or "explain")
    return {"reply": reply}

@app.get("/api/resources/{topicId}")
def get_topic_resources(topicId: str):
    return get_resources_for_topic(topicId)

# ---------------------------------------------------------------------------
# 7. Employee Dashboard Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/dashboard/{userId}")
def get_dashboard_summary(userId: str, role: Optional[str] = "Software Engineer"):
    db = SessionLocal()
    try:
        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == userId).first()
        if not profile:
            profile = UserProfileModel(user_id=userId, xp=0, level=1, streak_days=1)
            db.add(profile)
            db.commit()
            db.refresh(profile)
            
        role_topics = get_role_topics(role)
        states = db.query(UserTopicState).filter(UserTopicState.user_id == userId).all()
        
        mastered_count = sum(1 for s in states if s.difficulty == "Expert" and s.topic_id in role_topics)
        total_topics = len(role_topics)
        readiness_pct = int((mastered_count / total_topics) * 100) if total_topics > 0 else 0
        
        badges_list = json.loads(profile.badges) if profile.badges else []
        weak_areas = [
            {"topic_id": s.topic_id, "title": TOPICS.get(s.topic_id, {}).get("title", s.topic_id), "mastery": s.mastery_score}
            for s in states if s.status in ["Needs-Review"] or (s.mastery_score < 50 and s.status == "Current")
        ]
        
        return {
            "userId": userId,
            "level": profile.level,
            "xp": profile.xp,
            "xp_next_level": (profile.level * 100),
            "streak_days": profile.streak_days,
            "badges": badges_list,
            "readiness_percentage": readiness_pct,
            "mastered_count": mastered_count,
            "total_topics": total_topics,
            "weak_areas": weak_areas
        }
    finally:
        db.close()

# ---------------------------------------------------------------------------
# 8. Manager Readiness & Team Oversight Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/buddy/{username}/attention")
def buddy_attention(username: str):
    """Buddies see their assigned learners' weak areas (nudge digest, no email infra needed)."""
    adb = AuthSessionLocal()
    db = SessionLocal()
    try:
        learners = adb.query(UserAuthModel).filter(UserAuthModel.buddy_username == username).all()
        out = []
        for u in learners:
            states = db.query(UserTopicState).filter(UserTopicState.user_id == u.username).all()
            weak = [{"topic_id": s.topic_id, "mastery": s.mastery_score}
                    for s in states if s.status == "Needs-Review" or (s.status == "Current" and s.mastery_score < 50)]
            out.append({"userId": u.username, "name": u.full_name, "role": u.role, "weak_areas": weak})
        return out
    finally:
        adb.close()
        db.close()

@app.get("/api/manager/team")
def get_manager_team():
    db = SessionLocal()
    adb = AuthSessionLocal()
    try:
        auth_users = {u.username: u for u in adb.query(UserAuthModel).all()}
        profiles = db.query(UserProfileModel).all()
        
        team = []
        for p in profiles:
            u_info = auth_users.get(p.user_id)
            role = u_info.role if u_info else "Software Engineer"
            name = u_info.full_name if u_info else p.user_id.replace("_", " ").title()
            dept = u_info.department if u_info else "Engineering"
            
            required_topics = list(get_role_topics(role).keys())
            states = db.query(UserTopicState).filter(UserTopicState.user_id == p.user_id).all()
            r_data = compute_readiness(states, required_topics)
            
            team.append({
                "userId": p.user_id,
                "name": name,
                "role": role,
                "department": dept,
                "level": p.level,
                "xp": p.xp,
                "streak": p.streak_days,
                "readiness_score": r_data["score"],
                "status": r_data["status"],
                "missing_topics": [TOPICS.get(m, {}).get("title", m) for m in r_data["missing"]],
                "expert_count": r_data["expert_count"]
            })
        return team
    finally:
        db.close()
        adb.close()

@app.get("/api/manager/report/{userId}")
def get_employee_readiness_report(userId: str, role: Optional[str] = "Software Engineer"):
    db = SessionLocal()
    try:
        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == userId).first()
        if not profile:
            profile = UserProfileModel(user_id=userId)
            
        states = db.query(UserTopicState).filter(UserTopicState.user_id == userId).all()
        required_topics = list(get_role_topics(role).keys())
        r_data = compute_readiness(states, required_topics)

        signoffs = db.query(SignoffModel).filter(SignoffModel.user_id == userId).all()
        signoff_list = [{"topicId": s.topic_id, "signer": s.signer, "note": s.note,
                         "at": s.created_at.isoformat() if s.created_at else None} for s in signoffs]
        expert_topics = {s.topic_id for s in states if s.difficulty == "Expert"}
        signed_topics = {s["topicId"] for s in signoff_list if s["topicId"]}
        verified_topics = sorted(expert_topics & signed_topics)

        report_md = generate_readiness_report_md(profile, r_data, states, role)
        return {
            "userId": userId,
            "role": role,
            "readiness": r_data,
            "report_markdown": report_md,
            "signoffs": signoff_list,
            "verified_topics": verified_topics
        }
    finally:
        db.close()

# ---------------------------------------------------------------------------
# 9. Admin Knowledge Base & Feedback Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/admin/docs")
def list_documents():
    db = SessionLocal()
    try:
        docs = db.query(DocumentModel).all()
        return [
            {
                "id": d.id,
                "filename": d.filename,
                "title": d.title,
                "role": d.role,
                "status": d.status,
                "chunk_count": d.chunk_count,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                "owner": getattr(d, "owner", "") or "",
                "version": getattr(d, "version", 1) or 1,
                "review_after": d.review_after.isoformat() if getattr(d, "review_after", None) else None
            }
            for d in docs
        ]
    finally:
        db.close()

@app.post("/api/admin/docs/toggle/{docId}")
def toggle_document_status(docId: int):
    db = SessionLocal()
    try:
        doc = db.query(DocumentModel).filter(DocumentModel.id == docId).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.status == "draft":
            raise HTTPException(status_code=400, detail="Draft must be approved, not toggled")
        doc.status = "inactive" if doc.status == "active" else "active"
        db.commit()
        try:
            from services.embedding import set_document_status
            set_document_status(doc.id, doc.chunk_count, doc.status,
                                {"title": doc.title, "role": doc.role})
        except Exception as e:
            print("ChromaDB toggle warning:", e)
        return {"id": doc.id, "status": doc.status}
    finally:
        db.close()

@app.delete("/api/admin/docs/{docId}")
def delete_document(docId: int):
    db = SessionLocal()
    try:
        doc = db.query(DocumentModel).filter(DocumentModel.id == docId).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        try:
            delete_document_from_chroma(doc.id)
        except Exception as e:
            print("ChromaDB delete warning:", e)
        db.delete(doc)
        db.commit()
        return {"success": True, "deleted_id": docId}
    finally:
        db.close()

@app.post("/api/admin/docs/upload")
async def upload_document(file: UploadFile = File(...), owner: str = Form("")):
    file_bytes = await file.read()
    text = extract_text(file_bytes, file.filename)
    meta = extract_metadata_from_text(text)
    chunks = chunk_text(text)

    db = SessionLocal()
    try:
        new_doc = DocumentModel(
            filename=file.filename,
            title=meta["title"],
            role=meta["role"],
            status="draft",
            chunk_count=len(chunks),
            owner=(owner or "").strip()
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        # ChromaDB index (draft: invisible to retrieval until approved)
        ids = [f"doc_{new_doc.id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": str(new_doc.id), "title": meta["title"], "role": meta["role"], "status": "draft"} for _ in chunks]
        add_chunks_to_chroma(chunks, metadatas, ids)

        return {
            "success": True,
            "document": {
                "id": new_doc.id,
                "title": new_doc.title,
                "role": new_doc.role,
                "chunk_count": new_doc.chunk_count,
                "status": new_doc.status,
                "owner": new_doc.owner,
                "version": new_doc.version
            }
        }
    finally:
        db.close()

@app.post("/api/admin/docs/approve/{docId}")
def approve_document(docId: int, admin: str = Depends(_admin_guard)):
    """Review gate: draft -> active. New endpoint, guarded from day one."""
    from datetime import timedelta
    from services.embedding import set_document_status
    db = SessionLocal()
    try:
        doc = db.query(DocumentModel).filter(DocumentModel.id == docId).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc.status = "active"
        doc.review_after = datetime.utcnow() + timedelta(days=90)
        db.commit()
        try:
            set_document_status(doc.id, doc.chunk_count, "active",
                                {"title": doc.title, "role": doc.role})
        except Exception as e:
            print("ChromaDB approve warning:", e)
        # Stale mastery expires: Completed states on affected topics reopen
        # for review, since they were earned against the old SOP version.
        invalidated = 0
        try:
            from services.taxonomy import doc_topics_for_title
            for topic_key in doc_topics_for_title(doc.title):
                rows = db.query(UserTopicState).filter(
                    UserTopicState.topic_id == topic_key,
                    UserTopicState.status == "Completed"
                ).all()
                for s in rows:
                    s.status = "Needs-Review"
                    s.next_review_at = datetime.utcnow()
                invalidated += len(rows)
            db.commit()
        except Exception as e:
            print("Mastery expiry warning:", e)
        return {"id": doc.id, "status": doc.status,
                "review_after": doc.review_after.isoformat() if doc.review_after else None,
                "mastery_invalidated": invalidated}
    finally:
        db.close()

@app.get("/api/admin/feedback")
def list_feedback():
    db = SessionLocal()
    try:
        feedbacks = db.query(QuizFeedbackModel).order_by(QuizFeedbackModel.submitted_at.desc()).all()
        return [
            {
                "id": f.id,
                "question_text": f.question_text,
                "reason": f.reason,
                "feedback_text": f.feedback_text,
                "submitted_at": f.submitted_at.isoformat() if f.submitted_at else None
            }
            for f in feedbacks
        ]
    finally:
        db.close()

# ---------------------------------------------------------------------------
# 10. Admin portal — separate login + user CRUD (append-only, v1 untouched)
# ---------------------------------------------------------------------------
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminCreateUserRequest(BaseModel):
    username: str
    email: str
    password: Optional[str] = None
    full_name: str
    role: Optional[str] = "Software Engineer"
    department: Optional[str] = "Engineering"
    buddy: Optional[str] = ""

class AdminUpdateUserRequest(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    buddy: Optional[str] = None

def _public_user(u) -> Dict[str, Any]:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "department": u.department,
        "is_admin": u.is_admin,
        "buddy": getattr(u, "buddy_username", "") or "",
    }

@app.post("/api/admin/login")
def admin_login(req: AdminLoginRequest):
    db = AuthSessionLocal()
    try:
        user = db.query(UserAuthModel).filter(
            UserAuthModel.username == req.username
        ).first()
        if not user or not user.is_admin or not verify_password(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        return {
            "success": True,
            "user": _public_user(user),
            "token": f"admin_token_{user.username}_{user.id}",
        }
    finally:
        db.close()

@app.get("/api/admin/users")
def admin_list_users(admin: str = Depends(_admin_guard)):
    db = AuthSessionLocal()
    try:
        return [_public_user(u) for u in db.query(UserAuthModel).all()]
    finally:
        db.close()

@app.post("/api/admin/users")
def admin_create_user(req: AdminCreateUserRequest, admin: str = Depends(_admin_guard)):
    db = AuthSessionLocal()
    try:
        existing = db.query(UserAuthModel).filter(
            (UserAuthModel.username == req.username) | (UserAuthModel.email == req.email)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username or Email already exists")
        new_user = UserAuthModel(
            username=req.username,
            email=req.email,
            password_hash=hash_password(req.password or DEFAULT_EMPLOYEE_PASSWORD),
            full_name=req.full_name,
            role=req.role or "Software Engineer",
            department=req.department or "Engineering",
            is_admin=False,
            buddy_username=(req.buddy or "").strip(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        odb = SessionLocal()
        try:
            profile = odb.query(UserProfileModel).filter(UserProfileModel.user_id == new_user.username).first()
            if not profile:
                odb.add(UserProfileModel(user_id=new_user.username, xp=0, level=1, streak_days=1))
                odb.commit()
        finally:
            odb.close()
        return {"success": True, "user": _public_user(new_user)}
    finally:
        db.close()

@app.put("/api/admin/users/{username}")
def admin_update_user(username: str, req: AdminUpdateUserRequest, admin: str = Depends(_admin_guard)):
    db = AuthSessionLocal()
    try:
        user = db.query(UserAuthModel).filter(UserAuthModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if req.email is not None:
            user.email = req.email
        if req.full_name is not None:
            user.full_name = req.full_name
        if req.role is not None:
            user.role = req.role
        if req.department is not None:
            user.department = req.department
        if req.is_admin is not None:
            user.is_admin = req.is_admin
        if req.buddy is not None:
            user.buddy_username = (req.buddy or "").strip()
        if req.password:
            user.password_hash = hash_password(req.password)
        db.commit()
        db.refresh(user)
        return {"success": True, "user": _public_user(user)}
    finally:
        db.close()

@app.delete("/api/admin/users/{username}")
def admin_delete_user(username: str, admin: str = Depends(_admin_guard)):
    if username == admin:
        raise HTTPException(status_code=400, detail="Admin cannot delete self")
    adb = AuthSessionLocal()
    db = SessionLocal()
    try:
        user = adb.query(UserAuthModel).filter(UserAuthModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        adb.delete(user)
        adb.commit()
        db.query(UserTopicState).filter(UserTopicState.user_id == username).delete()
        profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == username).first()
        if profile:
            db.delete(profile)
        db.commit()
        return {"success": True, "deleted": username}
    finally:
        adb.close()
        db.close()

@app.post("/api/admin/users/{username}/reset-baseline")
def admin_reset_baseline(username: str, admin: str = Depends(_admin_guard)):
    """Clear a user's topic states so the (v1 or v2) baseline can be retaken."""
    db = SessionLocal()
    try:
        db.query(UserTopicState).filter(UserTopicState.user_id == username).delete()
        db.commit()
        return {"success": True, "reset": username}
    finally:
        db.close()

class TransferRequest(BaseModel):
    new_role: str
    new_department: Optional[str] = None

@app.post("/api/admin/users/{username}/transfer")
def admin_transfer_role(username: str, req: TransferRequest, admin: str = Depends(_admin_guard)):
    """Role transfer keeps shared-topic mastery, drops the rest. Growth stops nuking history."""
    from services.taxonomy import get_role_card
    adb = AuthSessionLocal()
    db = SessionLocal()
    try:
        user = adb.query(UserAuthModel).filter(UserAuthModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        old_topics = set(get_role_card(user.role).get("topics", {}).keys())
        new_topics = set(get_role_card(req.new_role).get("topics", {}).keys())
        dropped = sorted(old_topics - new_topics)
        kept = sorted(old_topics & new_topics)
        if dropped:
            db.query(UserTopicState).filter(
                UserTopicState.user_id == username,
                UserTopicState.topic_id.in_(dropped)
            ).delete(synchronize_session=False)
            db.commit()
        user.role = req.new_role
        if req.new_department is not None:
            user.department = req.new_department
        adb.commit()
        return {"success": True, "user": _public_user(user), "kept_topics": kept, "dropped_topics": dropped}
    finally:
        adb.close()
        db.close()

# ---------------------------------------------------------------------------
# 11. Adaptive quiz v2 — wrappers around frozen v1 (append-only)
# ---------------------------------------------------------------------------
@app.get("/api/v2/diagnostic/questions")
def v2_diagnostic_questions(role: Optional[str] = "Software Engineer", per_topic: Optional[int] = 3, userId: Optional[str] = None):
    profile = None
    if userId:
        try:
            from services.resume_profile import get_profile
            profile = get_profile(userId)
        except Exception:
            profile = None
    return get_baseline_questions(role=role or "Software Engineer", per_topic=per_topic or 3, profile=profile)

@app.post("/api/v2/diagnostic/evaluate")
def v2_diagnostic_evaluate(req: DiagnosticSubmitRequest):
    profile = None
    try:
        from services.resume_profile import get_profile
        profile = get_profile(req.userId)
    except Exception:
        profile = None
    return score_baseline(req.answers, role=req.role, profile=profile)

@app.get("/api/v2/quiz/next")
def v2_quiz_next(userId: str, role: Optional[str] = "Software Engineer"):
    card = get_role_card(role or "Software Engineer")
    required = list(card.get("topics", {}).keys())
    db = SessionLocal()
    try:
        states = db.query(UserTopicState).filter(UserTopicState.user_id == userId).all()
        weak = [s.topic_id for s in states
                if effective_mastery(s.mastery_score, s.last_attempt_at) < 50 and s.topic_id in required]
        mastery = min([effective_mastery(s.mastery_score, s.last_attempt_at)
                        for s in states if s.topic_id in required], default=0)
        difficulty = pick_difficulty(mastery)
        reason_suffix = ""
        if not states:
            # First session with a resume profile: start from calibrated floor.
            try:
                from services.resume_profile import get_profile
                prof = get_profile(userId)
                floors = [a.get("start_difficulty", "Beginner") for a in (prof or {}).get("topic_adjustments", {}).values()]
                if floors:
                    order = ["Beginner", "Intermediate", "Expert"]
                    difficulty = sorted(floors, key=order.index)[-1]
                    reason_suffix = " (resume-calibrated start)"
            except Exception:
                pass
        nxt = pick_next_topic(weak, states=states, required_topics=required)
        return {**nxt, "difficulty": difficulty, "role": role, "reason": nxt.get("reason", "") + reason_suffix}
    finally:
        db.close()

@app.get("/api/v2/quiz/generate")
def v2_quiz_generate(topic: str, role: Optional[str] = "all", userId: Optional[str] = None):
    mastery = 0
    if userId:
        db = SessionLocal()
        try:
            st = db.query(UserTopicState).filter(
                UserTopicState.user_id == userId, UserTopicState.topic_id == topic
            ).first()
            mastery = st.mastery_score if st else 0
        finally:
            db.close()
    return generate_personalized_quiz(topic, role=role or "all", mastery_score=mastery)

@app.get("/api/v2/quiz/session")
def v2_quiz_session(topic: str, role: Optional[str] = "all", userId: Optional[str] = None, count: Optional[int] = 20):
    """20-question no-repeat session at auto difficulty. Single-question v2 generate untouched."""
    from services.quiz_generator import generate_quiz_session
    mastery = 0
    if userId:
        db = SessionLocal()
        try:
            st = db.query(UserTopicState).filter(
                UserTopicState.user_id == userId, UserTopicState.topic_id == topic
            ).first()
            mastery = st.mastery_score if st else 0
        finally:
            db.close()
    session = generate_quiz_session(topic, role=role or "all", difficulty=pick_difficulty(mastery), count=count or 20)
    session["personalization"] = {"reason": f"mastery {mastery} -> {session['difficulty']}", "target_difficulty": session["difficulty"]}
    if userId:
        try:
            from services.eval_seen import log_seen
            log_seen(userId, [q.get("question", "") for q in session["questions"]])
        except Exception:
            pass
    return session

class EvalSubmitRequest(BaseModel):
    userId: str
    role: Optional[str] = "Software Engineer"
    answers: Dict[str, str]

class SignoffRequest(BaseModel):
    userId: str
    signer: str
    topicId: Optional[str] = None
    note: Optional[str] = ""

@app.post("/api/manager/signoff")
def manager_signoff(req: SignoffRequest):
    """Human evidence for Expert: signer must be an admin or the user's assigned buddy."""
    adb = AuthSessionLocal()
    db = SessionLocal()
    try:
        target = adb.query(UserAuthModel).filter(UserAuthModel.username == req.userId).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        signer_user = adb.query(UserAuthModel).filter(UserAuthModel.username == req.signer).first()
        is_admin = bool(signer_user and signer_user.is_admin)
        is_buddy = (target.buddy_username or "") == req.signer
        if not (is_admin or is_buddy):
            raise HTTPException(status_code=403, detail="Only an admin or the assigned buddy can sign off")
        row = SignoffModel(user_id=req.userId, topic_id=req.topicId,
                           signer=req.signer, note=req.note or "")
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"success": True, "signoff": {"id": row.id, "userId": row.user_id,
                "topicId": row.topic_id, "signer": row.signer, "note": row.note}}
    finally:
        adb.close()
        db.close()

@app.get("/api/v2/eval")
def v2_graded_eval(userId: str, role: Optional[str] = "Software Engineer", count: Optional[int] = 20):
    """Held-out graded assessment: unseen questions only. Answers stripped; server grades."""
    from services.quiz_generator import build_graded_eval
    from services.eval_seen import get_seen_hashes, log_seen
    built = build_graded_eval(role or "Software Engineer", get_seen_hashes(userId), count=count or 20)
    log_seen(userId, [q["question"] for q in built["questions"]])
    return {"role": role, **built}

@app.post("/api/v2/eval/submit")
def v2_eval_submit(req: EvalSubmitRequest):
    """Grade eval, update mastery via the standard (frozen) updater. No XP: measures don't pay."""
    from services.quiz_generator import grade_graded_eval
    result = grade_graded_eval(req.answers, role=req.role or "Software Engineer")
    db = SessionLocal()
    try:
        for eval_id, user_ans in (req.answers or {}).items():
            try:
                topic_key = eval_id.split(":", 1)[0]
            except ValueError:
                continue
            from services.diagnostic import is_answer_match
            from services.quiz_generator import _full_static_bank
            try:
                item = _full_static_bank(topic_key)[int(eval_id.split(":", 1)[1])]
            except (ValueError, IndexError):
                continue
            ok = is_answer_match(user_ans or "", item.get("correct_answer", ""))
            state = db.query(UserTopicState).filter(
                UserTopicState.user_id == req.userId,
                UserTopicState.topic_id == topic_key
            ).first()
            if not state:
                state = UserTopicState(user_id=req.userId, topic_id=topic_key,
                                       status="Current", difficulty="Beginner", mastery_score=0)
                db.add(state)
            update_topic_state(state, is_correct=ok)
        db.commit()
    finally:
        db.close()
    return {"success": True, **result}

@app.get("/api/taxonomy")
def get_taxonomy():
    return {"departments": DEPARTMENTS, "role_cards": ROLE_CARDS}

# ---------------------------------------------------------------------------
# 12. Resume-calibrated hybrid quiz (Phase C — append-only, v1/v2 defaults unchanged)
# ---------------------------------------------------------------------------
@app.post("/api/v2/profile/resume")
async def v2_upload_resume(
    userId: str = Form(...),
    role: str = Form(...),
    file: UploadFile = File(...),
    admin: str = Depends(_admin_guard),
):
    """Admin uploads a hire's resume. Raw text is never stored, logged, or indexed."""
    from services.resume_profile import extract_profile, map_to_role_card, save_profile

    file_bytes = await file.read()
    try:
        text = extract_text(file_bytes, file.filename or "resume.txt")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse resume file (PDF/DOCX/TXT only)")
    profile = extract_profile(text)
    if not profile:
        raise HTTPException(status_code=422, detail="No usable signal in resume — baseline will use the default role card")
    adjustments = map_to_role_card(profile, role)
    record = save_profile(userId, role, profile, adjustments)
    return {"success": True, "profile": record}

@app.get("/api/v2/profile/{userId}")
def v2_get_profile(userId: str, admin: str = Depends(_admin_guard)):
    from services.resume_profile import get_profile

    record = get_profile(userId)
    if not record:
        raise HTTPException(status_code=404, detail="No resume profile for user")
    return record

@app.delete("/api/v2/profile/{userId}")
def v2_delete_profile(userId: str, admin: str = Depends(_admin_guard)):
    from services.resume_profile import delete_profile

    if not delete_profile(userId):
        raise HTTPException(status_code=404, detail="No resume profile for user")
    return {"success": True, "deleted": userId}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
