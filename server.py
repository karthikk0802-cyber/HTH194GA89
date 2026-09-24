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
    get_db, DocumentModel, QuizFeedbackModel, UserTopicState, UserProfileModel, SessionLocal
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
def register_user(req: RegisterRequest):
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
                "is_admin": user.is_admin
            },
            "token": f"token_{user.username}_{user.id}"
        }
    finally:
        db.close()

@app.get("/api/auth/users")
def get_auth_users():
    """List all accounts for convenient quick-switch in the frontend."""
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
    bypassed = eval_data["bypassed_topics"]
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
            
        xp_to_add = eval_data.get("xp_to_award", (eval_data.get("correct_count", 0) * 10) + 50)
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
        
        report_md = generate_readiness_report_md(profile, r_data, states, role)
        return {
            "userId": userId,
            "role": role,
            "readiness": r_data,
            "report_markdown": report_md
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
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None
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
        doc.status = "inactive" if doc.status == "active" else "active"
        db.commit()
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
async def upload_document(file: UploadFile = File(...)):
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
            chunk_count=len(chunks)
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        # ChromaDB index
        ids = [f"doc_{new_doc.id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": str(new_doc.id), "title": meta["title"], "role": meta["role"]} for _ in chunks]
        add_chunks_to_chroma(chunks, metadatas, ids)
        
        return {
            "success": True,
            "document": {
                "id": new_doc.id,
                "title": new_doc.title,
                "role": new_doc.role,
                "chunk_count": new_doc.chunk_count
            }
        }
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
