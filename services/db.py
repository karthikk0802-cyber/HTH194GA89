import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./onboardiq.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentModel(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    title = Column(String)
    role = Column(String)
    status = Column(String, default="active") # active, inactive
    version = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class QuizFeedbackModel(Base):
    __tablename__ = "quiz_feedback"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String)
    reason = Column(String) # outdated, conflict, unclear
    feedback_text = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class UserTopicState(Base):
    __tablename__ = "user_topic_states"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, default="demo_user")
    topic_id = Column(String, index=True)
    status = Column(String, default="Locked") # Locked, Current, Recommended, Needs-Review, Completed
    difficulty = Column(String, default="Beginner") # Beginner, Intermediate, Expert
    mastery_score = Column(Integer, default=0) # 0 to 100
    last_attempt_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, nullable=True)
    review_interval_days = Column(Integer, default=1) # 1, 3, 7, 14, 30

class UserProfileModel(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, default="demo_user")
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_login = Column(DateTime, nullable=True)
    badges = Column(String, default="[]") # JSON list


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
