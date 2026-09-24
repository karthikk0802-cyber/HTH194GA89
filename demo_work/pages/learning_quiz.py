import streamlit as st
from services.db import get_db, QuizFeedbackModel
from services.quiz_generator import generate_quiz_for_topic
from services.quiz_validator import validate_quiz_question

st.set_page_config(page_title="Learning Quiz", page_icon="📝", layout="wide")
st.title("Grounded Learning Quiz")

topic = st.selectbox("Select Topic to Practice:", ["Security & Compliance", "Git Workflow", "Deployment & CI/CD", "Company Basics"])
role = st.selectbox("Your Role:", ["all", "engineering", "devops"])

if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None

if st.button("Generate Quiz Question"):
    with st.spinner("Generating and Validating Question..."):
        quiz = generate_quiz_for_topic(topic, role=role)
        
        if "error" in quiz:
            if quiz["error"] == "INSUFFICIENT_EVIDENCE":
                st.error("Cannot generate quiz: INSUFFICIENT_EVIDENCE in knowledge base for this topic.")
            else:
                st.error(quiz["error"])
        else:
            # Validate
            is_valid = validate_quiz_question(quiz, quiz.get("evidence_quote"))
            if not is_valid:
                st.error("Generated question failed the validation gate (Hallucination/Ambiguity detected). Please try again.")
            else:
                st.session_state.current_quiz = quiz
                st.rerun()

if st.session_state.current_quiz:
    quiz = st.session_state.current_quiz
    st.markdown("---")
    st.markdown(f"### {quiz['question']}")
    
    with st.expander("Show Question Metadata"):
        st.write(f"**Learning Objective:** {quiz.get('learning_objective')}")
        st.write(f"**Citations:** {', '.join(quiz.get('citations', []))}")
        
    user_ans = st.radio("Select your answer:", quiz["options"], index=None)
    
    if st.button("Submit Answer"):
        if user_ans == quiz["correct_answer"]:
            st.success("Correct!")
            st.info(f"**Evidence:** {quiz.get('evidence_quote')}")
            st.session_state.remediation = None
        else:
            st.error(f"Incorrect. The correct answer was: **{quiz['correct_answer']}**")
            with st.spinner("Generating personalized explanation..."):
                from services.teaching import generate_remediation, generate_explain_again
                remediation = generate_remediation(quiz["question"], user_ans, quiz["correct_answer"], quiz.get("evidence_quote"))
                st.session_state.remediation = remediation
                st.session_state.user_ans = user_ans
                st.session_state.explain_again = None

    if st.session_state.get("remediation"):
        rem = st.session_state.remediation
        if "error" not in rem:
            st.markdown("### Let's review!")
            st.write(f"**Why your answer was incorrect:** {rem.get('why_incorrect')}")
            st.write(f"**Why the correct answer is right:** {rem.get('why_correct')}")
            st.info(f"💡 **Memory Hook:** {rem.get('memory_hook')}")
            st.write(f"📖 **Quoted Policy:** {quiz.get('evidence_quote')}")
            
            if st.button("Still confused? Explain Again (Simpler)"):
                with st.spinner("Finding another way to explain..."):
                    from services.teaching import generate_explain_again
                    prev_exp = f"{rem.get('why_incorrect')} {rem.get('why_correct')}"
                    st.session_state.explain_again = generate_explain_again(
                        quiz["question"], st.session_state.user_ans, quiz["correct_answer"], prev_exp
                    )
                    
        if st.session_state.get("explain_again"):
            st.warning("### Alternate Explanation")
            st.write(st.session_state.explain_again)
            
    st.markdown("---")
    st.markdown("#### Feedback")
    with st.form("feedback_form"):
        st.write("Was this question unhelpful or inaccurate?")
        reason = st.selectbox("Reason", ["Outdated", "Conflict with other policy", "Unclear/Ambiguous"])
        comments = st.text_area("Additional Comments")
        if st.form_submit_button("Submit Feedback"):
            db = next(get_db())
            feedback = QuizFeedbackModel(
                question_text=quiz["question"],
                reason=reason,
                feedback_text=comments
            )
            db.add(feedback)
            db.commit()
            st.success("Feedback submitted for admin review!")
