import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.db import get_db, UserProfileModel, UserTopicState
import json
from datetime import datetime, timedelta


def seed_demo_users():
    db = next(get_db())
    
    # Pre-clear old demo data
    db.query(UserProfileModel).filter(UserProfileModel.user_id != "demo_user").delete()
    db.query(UserTopicState).filter(UserTopicState.user_id != "demo_user").delete()
    
    users = [
        {"id": "sarah_engineer", "level": 3, "xp": 350, "streak": 5, "badges": ["First Mastery"]},
        {"id": "mike_devops", "level": 1, "xp": 45, "streak": 1, "badges": []},
        {"id": "alex_pm", "level": 5, "xp": 520, "streak": 14, "badges": ["Week Warrior", "Scholar"]},
        {"id": "jessica_sales", "level": 2, "xp": 180, "streak": 2, "badges": []},
        {"id": "david_hr", "level": 1, "xp": 10, "streak": 0, "badges": []},
        {"id": "emma_engineer", "level": 4, "xp": 490, "streak": 8, "badges": ["Week Warrior"]},
        {"id": "chris_support", "level": 2, "xp": 210, "streak": 3, "badges": ["First Mastery"]},
        {"id": "lisa_data", "level": 1, "xp": 0, "streak": 0, "badges": []}
    ]
    
    for u in users:
        p = UserProfileModel(
            user_id=u["id"], xp=u["xp"], level=u["level"], streak_days=u["streak"],
            badges=json.dumps(u["badges"]), last_login=datetime.utcnow() - timedelta(days=1)
        )
        db.add(p)
        
        # Add varied topic states depending on user
        if u["id"] == "sarah_engineer":
            # Almost ready
            for t in ["company_basics", "security", "tools", "git_workflow"]:
                db.add(UserTopicState(user_id=u["id"], topic_id=t, status="Completed", difficulty="Expert", mastery_score=85))
            db.add(UserTopicState(user_id=u["id"], topic_id="architecture", status="Current", difficulty="Intermediate", mastery_score=60))
            
        elif u["id"] == "mike_devops":
            # Just starting
            db.add(UserTopicState(user_id=u["id"], topic_id="company_basics", status="Current", difficulty="Beginner", mastery_score=15))
            
        elif u["id"] == "alex_pm":
            # Fully ready
            for t in ["company_basics", "security", "tools", "product_triage"]:
                db.add(UserTopicState(user_id=u["id"], topic_id=t, status="Completed", difficulty="Expert", mastery_score=95))
                
    db.commit()
    print("Seeded 8 demo users with varied histories successfully.")

if __name__ == "__main__":
    seed_demo_users()
