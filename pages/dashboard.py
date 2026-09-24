import streamlit as st
import json
import pandas as pd
from services.db import get_db, UserProfileModel, UserTopicState
from services.roles import TOPICS, get_role_topics
from services.gamification import check_streak, update_badges

st.set_page_config(page_title="My Dashboard", page_icon="📈", layout="wide")

st.title("Employee Dashboard")

db = next(get_db())

# Ensure profile exists
profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == "demo_user").first()
if not profile:
    profile = UserProfileModel(user_id="demo_user")
    db.add(profile)
    db.commit()

# Update streak
check_streak(profile)
db.commit()

# Fetch States
role = "Software Engineer" # hardcoded for demo dashboard
role_topics = get_role_topics(role)
user_states = db.query(UserTopicState).filter(UserTopicState.user_id == "demo_user").all()

# Update Badges
new_badges = update_badges(profile, user_states)
if new_badges:
    for b in new_badges:
        st.toast(f"🏆 Achievement Unlocked: {b}!")
db.commit()

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Level", profile.level)
col2.metric("Total XP", profile.xp)
col3.metric("Day Streak 🔥", profile.streak_days)

mastered = sum(1 for s in user_states if s.difficulty == "Expert")
total = len(role_topics)
col4.metric("Role Readiness", f"{int((mastered/total)*100) if total > 0 else 0}%")

st.markdown("---")

# Split view
left, right = st.columns([2, 1])

with left:
    st.subheader("Your Learning Roadmap")
    # Visual roadmap
    roadmap_data = []
    for topic_id, data in role_topics.items():
        state = next((s for s in user_states if s.topic_id == topic_id), None)
        status = state.status if state else "Locked"
        mastery = state.mastery_score if state else 0
        roadmap_data.append({"Topic": data["title"], "Status": status, "Mastery": f"{mastery}/100"})
        
    df = pd.DataFrame(roadmap_data)
    st.table(df)

with right:
    st.subheader("Achievements")
    badges = json.loads(profile.badges)
    if badges:
        for b in badges:
            st.success(f"🏅 {b}")
    else:
        st.info("Complete modules and maintain streaks to earn badges!")
        
    st.markdown("---")
    st.subheader("Weak Areas (Needs Review)")
    weak_areas = [s for s in user_states if s.status == "Needs-Review"]
    if weak_areas:
        for w in weak_areas:
            st.warning(f"⚠️ {TOPICS[w.topic_id]['title']}")
    else:
        st.write("No weak areas identified currently.")
