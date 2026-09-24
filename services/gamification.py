import json
from datetime import datetime, timedelta

def award_xp(profile, action, score=None):
    """Award XP based on action and score, update levels and badges."""
    xp_gained = 0
    if action == "quiz_correct":
        xp_gained = 15
    elif action == "scenario_completed":
        xp_gained = 50 + (score // 2 if score else 0)
    elif action == "daily_login":
        xp_gained = 10
        
    profile.xp += xp_gained
    
    # Calculate Level (Every 100 XP is a level)
    new_level = (profile.xp // 100) + 1
    if new_level > profile.level:
        profile.level = new_level
        
    return xp_gained

def check_streak(profile):
    """Check and update login streaks."""
    now = datetime.utcnow()
    if not profile.last_login:
        profile.streak_days = 1
    else:
        delta = now - profile.last_login
        if delta.days == 1:
            profile.streak_days += 1
        elif delta.days > 1:
            profile.streak_days = 1 # Reset streak
            
    profile.last_login = now
    
def update_badges(profile, user_states):
    """Check for new achievements/badges."""
    current_badges = json.loads(profile.badges)
    new_badges = []
    
    # Check mastery badges
    expert_count = sum(1 for s in user_states if s.difficulty == "Expert")
    if expert_count >= 1 and "First Mastery" not in current_badges:
        new_badges.append("First Mastery")
    if expert_count >= 5 and "Scholar" not in current_badges:
        new_badges.append("Scholar")
        
    # Check streak badges
    if profile.streak_days >= 7 and "Week Warrior" not in current_badges:
        new_badges.append("Week Warrior")
        
    if new_badges:
        current_badges.extend(new_badges)
        profile.badges = json.dumps(current_badges)
        
    return new_badges
