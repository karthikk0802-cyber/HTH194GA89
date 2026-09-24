import streamlit as st
import plotly.graph_objects as go
from services.db import get_db, UserTopicState
from services.roles import TOPICS, get_role_topics
from services.adaptive import build_competency_graph, rank_next_topics

st.set_page_config(page_title="Learning Path", page_icon="🗺️", layout="wide")

st.title("Your Learning Path")
st.markdown("Your personalized, deterministic roadmap.")

# Mock user data for UI demonstration
db = next(get_db())
role = st.selectbox("Simulate View for Role:", ["Software Engineer", "DevOps Engineer", "Sales Representative"])
role_topics = get_role_topics(role)

# Fetch user states
user_states = db.query(UserTopicState).filter(UserTopicState.user_id == "demo_user").all()

# Seed states if empty for demo purposes
if not user_states:
    for t_id in role_topics:
        new_state = UserTopicState(user_id="demo_user", topic_id=t_id)
        if t_id == "company_basics":
            new_state.status = "Current"
        db.add(new_state)
    db.commit()
    user_states = db.query(UserTopicState).filter(UserTopicState.user_id == "demo_user").all()

ranked_topics = rank_next_topics(user_states, list(role_topics.keys()))

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Today's Focus")
    if ranked_topics:
        top = ranked_topics[0]
        topic_info = role_topics[top["topic_id"]]
        st.success(f"### {topic_info['title']}\n**Why am I learning this next?** {top['reason']}")
        st.button("Start Module", type="primary")
        
        st.markdown("---")
        st.subheader("Up Next")
        for t in ranked_topics[1:4]:
            t_info = role_topics[t["topic_id"]]
            st.info(f"**{t_info['title']}** - {t['status']}")
    else:
        st.success("🎉 You've mastered all required topics for your role! Come back later for reviews.")

with col2:
    st.subheader("Competency Mastery")
    state_map = {s.topic_id: s for s in user_states}
    
    # Plotly visualization of mastery
    categories = [role_topics[t]["title"] for t in role_topics]
    scores = [state_map.get(t).mastery_score if state_map.get(t) else 0 for t in role_topics]
    
    fig = go.Figure(data=[
        go.Bar(name='Mastery', x=scores, y=categories, orientation='h', marker_color='#4f46e5')
    ])
    fig.update_layout(xaxis_range=[0, 100], margin=dict(l=0, r=0, t=30, b=0), height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
with st.expander("View Competency Graph (Admin/Debug)"):
    import networkx as nx
    G = build_competency_graph()
    edges = list(G.edges())
    st.write("Current prerequisite edges tracking deterministic dependencies:")
    for edge in edges:
        st.write(f"- `{edge[0]}` ➔ `{edge[1]}`")
