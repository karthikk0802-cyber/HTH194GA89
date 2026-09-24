import streamlit as st
from services.scenarios import SCENARIOS, evaluate_scenario_response
from services.resources import get_resources_for_topic
from services.voice import handle_voice_interaction
from services.embedding import search_chroma
from services.db import get_db, UserTopicState

st.set_page_config(page_title="Scenarios & Voice", page_icon="🎙️", layout="wide")

st.title("Applied Learning: Scenarios & Voice Tutor")

tab1, tab2, tab3 = st.tabs(["🧩 Scenario Practice", "🎙️ Voice Tutor", "📚 Trusted Resources"])

# TAB 1: SCENARIOS
with tab1:
    st.subheader("Scenario-Based Training")
    selected_scen_id = st.selectbox("Select a Scenario:", list(SCENARIOS.keys()), format_func=lambda x: SCENARIOS[x]["title"])
    scenario = SCENARIOS[selected_scen_id]
    
    st.info(f"**Situation:** {scenario['text']}")
    
    user_response = st.text_area("Your Response: Walk through your exact steps.")
    
    if st.button("Submit Scenario Response") and user_response:
        with st.spinner("Evaluating across 4 dimensions..."):
            # Fetch evidence for context
            results = search_chroma(f"{scenario['topic_id']} policy guidelines", n_results=2)
            evidence = "\n".join(results['documents'][0]) if results and results['documents'] else "No specific evidence found."
            
            eval_data = evaluate_scenario_response(scenario['text'], user_response, evidence)
            
            if "error" in eval_data:
                st.error("Evaluation failed: " + eval_data["error"])
            else:
                st.markdown("### Evaluation Results")
                cols = st.columns(4)
                cols[0].metric("Policy Knowledge", f"{eval_data.get('policy_score', 0)}/10")
                cols[1].metric("Decision Quality", f"{eval_data.get('decision_score', 0)}/10")
                cols[2].metric("Procedure Adherence", f"{eval_data.get('procedure_score', 0)}/10")
                cols[3].metric("Risk Awareness", f"{eval_data.get('risk_score', 0)}/10")
                
                st.success(f"**Feedback:** {eval_data.get('feedback')}")
                st.info(f"**Mastery Impact:** +{eval_data.get('mastery_impact')} points added to {scenario['title']} topic.")

# TAB 2: VOICE TUTOR
with tab2:
    st.subheader("Interactive Voice Tutor")
    mode = st.radio("Tutor Mode:", ["explain", "quiz-me", "explain-mistake", "give-example", "what-next"], horizontal=True)
    
    st.markdown("*Note: Microphone WebRTC disabled in prototype environment. Using text fallback for graceful degradation.*")
    voice_sim = st.text_input("Simulate Voice Input (STT Fallback):")
    
    if st.button("Send to Tutor"):
        response = handle_voice_interaction(voice_sim, mode)
        st.success(response)

# TAB 3: CURATED RESOURCES
with tab3:
    st.subheader("Trusted Resources Library")
    st.markdown("Only verified, non-hallucinated resources from the admin catalog.")
    
    topic_res = st.selectbox("Select Topic to find resources:", ["company_basics", "security", "git_workflow", "tools"])
    resources = get_resources_for_topic(topic_res)
    
    if resources:
        for r in resources:
            st.markdown(f"- **[{r['type']}]** [{r['title']}]({r['url']})")
    else:
        st.write("No curated resources for this topic yet.")
