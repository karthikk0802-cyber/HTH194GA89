import os
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Dedicated Auth Database - completely separated from Chroma VectorDB and Knowledge Base DB
AUTH_DATABASE_URL = "sqlite:///./auth.db"
auth_engine = create_engine(AUTH_DATABASE_URL, connect_args={"check_same_thread": False})
AuthSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)
AuthBase = declarative_base()

class UserAuthModel(AuthBase):
    __tablename__ = "auth_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="Software Engineer") # Software Engineer, Product Manager, DevOps Engineer, Manager, Admin
    department = Column(String, default="Engineering")
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

AuthBase.metadata.create_all(bind=auth_engine)

def get_auth_db():
    db = AuthSessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = "nexora_onboardiq_secure_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def seed_default_auth_users():
    """Seed default authentication accounts into auth.db"""
    db = AuthSessionLocal()
    try:
        if db.query(UserAuthModel).count() == 0:
            demo_accounts = [
                {
                    "username": "sarah_engineer",
                    "email": "sarah@nexora.com",
                    "password": "password123",
                    "full_name": "Sarah Jenkins",
                    "role": "Software Engineer",
                    "department": "Core Platform",
                    "is_admin": False
                },
                {
                    "username": "alex_pm",
                    "email": "alex@nexora.com",
                    "password": "password123",
                    "full_name": "Alex Rivera",
                    "role": "Product Manager",
                    "department": "Product",
                    "is_admin": False
                },
                {
                    "username": "mike_devops",
                    "email": "mike@nexora.com",
                    "password": "password123",
                    "full_name": "Mike Chen",
                    "role": "DevOps Engineer",
                    "department": "Infrastructure",
                    "is_admin": False
                },
                {
                    "username": "manager",
                    "email": "manager@nexora.com",
                    "password": "password123",
                    "full_name": "Sadhana",
                    "role": "Manager",
                    "department": "Engineering Leadership",
                    "is_admin": True
                },
                {
                    "username": "admin",
                    "email": "admin@nexora.com",
                    "password": "admin123",
                    "full_name": "Karthik",
                    "role": "Admin",
                    "department": "IT & SecOps",
                    "is_admin": True
                }
            ]
            for acc in demo_accounts:
                user = UserAuthModel(
                    username=acc["username"],
                    email=acc["email"],
                    password_hash=hash_password(acc["password"]),
                    full_name=acc["full_name"],
                    role=acc["role"],
                    department=acc["department"],
                    is_admin=acc["is_admin"]
                )
                db.add(user)
            db.commit()
            print("Successfully seeded auth.db with default user accounts.")
    finally:
        db.close()

seed_default_auth_users()
