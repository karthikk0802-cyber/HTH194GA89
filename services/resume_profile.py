# Resume profile sidecar (Phase C1) — deterministic extraction, no new deps.
# Raw resume text is NEVER persisted, logged, or indexed. Only the extracted
# skills summary is stored, via the sqlite helpers below (own table, v1 untouched).

import json
import re
import sqlite3
from datetime import datetime, timezone

PROFILE_DB = "./onboardiq.db"

# keyword -> topic (role-card topics)
SKILL_TOPIC_MAP = {
    "git_workflow": ["git", "github", "gitlab", "pull request", "code review", "trunk", "ci pipeline", "gpg", "codeowners"],
    "deployment": ["kubernetes", "docker", "terraform", "jenkins", "ci/cd", "cicd", "aws", "gcp", "azure", "helm", "ansible", "sre", "on-call", "pagerduty", "canary"],
    "architecture": ["microservices", "grpc", "kafka", "postgresql", "postgres", "chromadb", "vector", "react", "node", "python", "go ", "golang", "rest api", "graphql", "redis", "system design"],
    "tools": ["slack", "jira", "confluence", "notion", "agile", "scrum", "figma", "workday", "expensify"],
    "product_triage": ["rice", "roadmap", "backlog", "user stories", "sprint planning", "a/b testing"],
    "sales_playbook": ["meddic", "quota", "sales pipeline", "prospecting", "discovery calls", "enterprise sales"],
    "security": ["sso", "mfa", "oauth", "gdpr", "encryption", "soc 2", "soc2", "penetration", "owasp", "vault"],
    "company_basics": ["onboarding", "handbook", "pto", "okrs", "all-hands"],
}

SENIOR_TITLES = ["senior", "sr.", "lead", "principal", "staff", "architect", "head of", "director", "vp"]
JUNIOR_TITLES = ["intern", "junior", "jr.", "trainee", "associate", "graduate"]

KNOWN_ROLES = [
    "Frontend Engineer", "Backend Engineer", "ML Engineer", "DevOps Engineer", "SRE",
    "Product Manager", "Product Designer", "Data Scientist", "Account Executive",
    "Marketing Specialist", "HR Manager", "Support Engineer", "IT Administrator",
    "Software Engineer", "Sales Representative",
]


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS user_resume_profile (
            user_id TEXT PRIMARY KEY,
            role TEXT,
            seniority TEXT,
            skills_json TEXT,
            years_by_skill_json TEXT,
            past_roles_json TEXT,
            topic_adjustments_json TEXT,
            confidence REAL,
            created_at TEXT
        )"""
    )


def extract_profile(text: str) -> dict | None:
    """Deterministic resume -> profile. Returns None when text has no usable signal."""
    if not text or len(text.strip()) < 200:
        return None
    lowered = text.lower()

    matched_topics: dict[str, list[str]] = {}
    for topic, keywords in SKILL_TOPIC_MAP.items():
        hits = [kw for kw in keywords if kw in lowered]
        if hits:
            matched_topics[topic] = hits
    if not matched_topics:
        return None

    years_found = [int(m) for m in re.findall(r"(\d{1,2})\s*(?:\+)?\s*years?", lowered)]
    years = max(years_found) if years_found else 0
    if any(t in lowered for t in SENIOR_TITLES):
        seniority = "senior"
    elif any(t in lowered for t in JUNIOR_TITLES):
        seniority = "junior"
    elif years >= 7:
        seniority = "senior"
    elif years >= 3:
        seniority = "mid"
    else:
        seniority = "junior"

    past_roles = [r for r in KNOWN_ROLES if r.lower() in lowered]
    skills = sorted({kw for hits in matched_topics.values() for kw in hits})
    confidence = min(0.95, 0.4 + 0.05 * len(skills) + (0.1 if years_found else 0.0))

    return {
        "seniority": seniority,
        "years_overall": years,
        "skills": skills,
        "topics": sorted(matched_topics.keys()),
        "past_roles": past_roles,
        "confidence": round(confidence, 2),
    }


def map_to_role_card(profile: dict | None, role: str) -> dict:
    """Resume -> per-topic calibration for a role card.

    Claimed topics get +1 baseline question (verify, don't trust) and a
    raised entry-difficulty floor (max Intermediate — never Expert without proof).
    Unknown role or no profile -> {} (today's behavior, byte-identical).
    """
    if not profile:
        return {}
    try:
        from services.taxonomy import get_role_card
    except Exception:
        return {}
    card = get_role_card(role)
    claimed = set(profile.get("topics", []))
    seniority = profile.get("seniority", "junior")
    floor = {"junior": "Beginner", "mid": "Intermediate", "senior": "Intermediate"}[seniority]

    adjustments: dict[str, dict] = {}
    for topic in card.get("topics", {}):
        if topic in claimed:
            adjustments[topic] = {"start_difficulty": floor, "extra_questions": 1}
    return adjustments


def save_profile(user_id: str, role: str, profile: dict, adjustments: dict) -> dict:
    record = {
        "user_id": user_id,
        "role": role,
        "seniority": profile.get("seniority", "junior"),
        "skills": profile.get("skills", []),
        "years_by_skill": {"overall": profile.get("years_overall", 0)},
        "past_roles": profile.get("past_roles", []),
        "topic_adjustments": adjustments,
        "confidence": profile.get("confidence", 0.0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = sqlite3.connect(PROFILE_DB)
    try:
        _ensure_table(conn)
        conn.execute(
            """INSERT INTO user_resume_profile
               (user_id, role, seniority, skills_json, years_by_skill_json,
                past_roles_json, topic_adjustments_json, confidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                 role=excluded.role, seniority=excluded.seniority,
                 skills_json=excluded.skills_json,
                 years_by_skill_json=excluded.years_by_skill_json,
                 past_roles_json=excluded.past_roles_json,
                 topic_adjustments_json=excluded.topic_adjustments_json,
                 confidence=excluded.confidence, created_at=excluded.created_at""",
            (
                record["user_id"], record["role"], record["seniority"],
                json.dumps(record["skills"]), json.dumps(record["years_by_skill"]),
                json.dumps(record["past_roles"]), json.dumps(record["topic_adjustments"]),
                record["confidence"], record["created_at"],
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return record


def get_profile(user_id: str) -> dict | None:
    conn = sqlite3.connect(PROFILE_DB)
    try:
        _ensure_table(conn)
        row = conn.execute(
            "SELECT user_id, role, seniority, skills_json, years_by_skill_json,"
            " past_roles_json, topic_adjustments_json, confidence, created_at"
            " FROM user_resume_profile WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    return {
        "user_id": row[0],
        "role": row[1],
        "seniority": row[2],
        "skills": json.loads(row[3] or "[]"),
        "years_by_skill": json.loads(row[4] or "{}"),
        "past_roles": json.loads(row[5] or "[]"),
        "topic_adjustments": json.loads(row[6] or "{}"),
        "confidence": row[7],
        "created_at": row[8],
    }


def delete_profile(user_id: str) -> bool:
    conn = sqlite3.connect(PROFILE_DB)
    try:
        _ensure_table(conn)
        cur = conn.execute("DELETE FROM user_resume_profile WHERE user_id = ?", (user_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
