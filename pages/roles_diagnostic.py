import streamlit as st
from services.roles import ROLES, get_role_topics
from services.diagnostic import DIAGNOSTIC_QUESTIONS, evaluate_diagnostic

st.set_page_config(page_title="Roles & Diagnostic", page_icon="📝", layout="wide")

st.title("Step 1: Role & Pre-Assessment")
st.markdown("Select your role and complete the diagnostic to personalize your onboarding path.")

# 1. Role Selection
st.subheader("1. Select Your Role")
selected_role = st.selectbox("I am joining Nexora as a:", [""] + ROLES)

if selected_role:
    st.success(f"Role confirmed: **{selected_role}**")
    role_topics = get_role_topics(selected_role)
    st.markdown("### Your Required Topics")
    for topic_id, data in role_topics.items():
        st.write(f"- **{data['title']}** (Prerequisites: {', '.join(data['prerequisites']) or 'None'})")

    # 2. Diagnostic Assessment
    st.markdown("---")
    st.subheader("2. Diagnostic Pre-Assessment")
    st.info("Let's see what you already know! We'll skip topics you've already mastered.")
    
    with st.form("diagnostic_form"):
        user_answers = {}
        for q in DIAGNOSTIC_QUESTIONS:
            st.markdown(f"**{q['question']}**")
            user_answers[q["id"]] = st.radio("Select an answer:", q["options"], key=q["id"], index=None)
            st.write("")
            
        submitted = st.form_submit_button("Submit Diagnostic")
        
        if submitted:
            # Check if all answered
            if None in user_answers.values():
                st.error("Please answer all questions before submitting.")
            else:
                bypassed = evaluate_diagnostic(user_answers)
                
                st.success("Diagnostic complete!")
                if bypassed:
                    st.write("### Demonstrated Competencies")
                    st.write("You have successfully demonstrated knowledge in the following topics. They will be marked as **Skipped** in your learning path:")
                    for t in bypassed:
                        # only skip if it's in their role path
                        if t in role_topics:
                            st.markdown(f"- ✅ **{role_topics[t]['title']}**")
                else:
                    st.write("No topics skipped. We'll start from the beginning!")
                    
                st.button("Continue to Learning Path", type="primary")
