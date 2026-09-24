import streamlit as st
import pandas as pd
from services.db import get_db, UserProfileModel, UserTopicState
from services.roles import ROLES, get_role_topics
from services.readiness import compute_readiness, generate_readiness_report_md

st.set_page_config(page_title="Manager Dashboard", page_icon="👥", layout="wide")

st.title("Team Readiness & Oversight")

# MOCK DATA FOR MANAGER VIEW
st.markdown("### Team Overview")

db = next(get_db())
# For the prototype, we treat the 'demo_user' as the team member
profiles = db.query(UserProfileModel).all()

team_data = []
for p in profiles:
    # Assuming role is Software Engineer for demo
    role = "Software Engineer"
    required = list(get_role_topics(role).keys())
    states = db.query(UserTopicState).filter(UserTopicState.user_id == p.user_id).all()
    r_data = compute_readiness(states, required)
    
    team_data.append({
        "Employee": p.user_id,
        "Role": role,
        "Level": p.level,
        "Readiness Score": f"{r_data['score']}/100",
        "Status": r_data['status']
    })

if team_data:
    st.table(pd.DataFrame(team_data))
    
    st.markdown("---")
    st.subheader("Drill Down & Export")
    selected_emp = st.selectbox("Select Employee:", [d["Employee"] for d in team_data])
    
    if selected_emp:
        p = db.query(UserProfileModel).filter(UserProfileModel.user_id == selected_emp).first()
        states = db.query(UserTopicState).filter(UserTopicState.user_id == selected_emp).all()
        required = list(get_role_topics("Software Engineer").keys())
        r_data = compute_readiness(states, required)
        
        st.write(f"**Current Status:** {r_data['status']}")
        if r_data["missing"]:
            st.warning(f"**Bottlenecks / Missing:** {', '.join(r_data['missing'])}")
            
        report_md = generate_readiness_report_md(p, r_data, states, "Software Engineer")
        st.download_button(
            label="📄 Export Readiness Report (PDF/MD)",
            data=report_md,
            file_name=f"{selected_emp}_readiness_report.md",
            mime="text/markdown"
        )
else:
    st.info("No team members found.")
