import streamlit as st
from services.rag import generate_rag_response

st.set_page_config(page_title="Knowledge Coach", page_icon="💡", layout="wide")

st.title("Knowledge Q&A")
st.markdown("Ask questions about Nexora policies and guidelines.")

# Simulated user role selection for testing RAG-04
selected_role = st.selectbox("Simulate Role:", ["all", "engineering", "product", "devops", "sales"])

query = st.text_input("Ask a question (e.g., 'What is our remote work policy?')")

if st.button("Ask") and query:
    with st.spinner("Searching knowledge base and consulting Mistral..."):
        trace = generate_rag_response(query, role=selected_role)
        
        # Display the Answer
        st.subheader("Answer")
        if trace["confidence"] == "Insufficient":
            st.warning(trace["answer"])
        else:
            st.success(trace["answer"])
            
        # Display Confidence Indicator
        conf_color = "green" if trace["confidence"] == "Strong" else "orange" if trace["confidence"] == "Moderate" else "red"
        st.markdown(f"**Evidence Confidence:** :{conf_color}[{trace['confidence']}]")
        
        # Debug / Transparency Panel
        with st.expander("Debug Trace & Citations (RAG Transparency)"):
            st.write(f"**Timestamp:** {trace['timestamp']}")
            st.write(f"**Query:** {trace['query']}")
            st.write("**Citations Used:**", ", ".join(list(set(trace['citations']))) if trace['citations'] else "None")
            st.markdown("### Retrieved Chunks:")
            for i, chunk in enumerate(trace["chunks"]):
                st.info(f"**{chunk['title']}** (Distance: {chunk['distance']:.3f})\n\n{chunk['text']}")
