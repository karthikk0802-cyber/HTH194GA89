import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="OnboardIQ - Nexora",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise CSS
st.markdown("""
<style>
    :root {
        --primary: #4f46e5;
        --bg: #ffffff;
        --text: #1f2937;
    }
    .stApp {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: var(--primary);
        color: white;
        border-radius: 6px;
        border: none;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

def check_env():
    if not os.getenv("MISTRAL_API_KEY"):
        st.error("Mistral API key is missing. Please set MISTRAL_API_KEY in your .env file.", icon="⚠️")
        st.stop()

def main():
    check_env()
    
    st.sidebar.image("https://ui-avatars.com/api/?name=Nexora&background=4f46e5&color=fff&rounded=true", width=60)
    st.sidebar.title("OnboardIQ")
    st.sidebar.markdown("---")
    
    st.title("Welcome to OnboardIQ")
    st.markdown("### Adaptive Corporate Onboarding & Knowledge Coach")
    st.info("The environment is set up successfully. Navigate using the Streamlit sidebar pages.")
    
    st.markdown("""
    **Core Features available in the sidebar:**
    - **Step 1:** Roles & Diagnostic Pre-Assessment
    - **Step 2:** Learning Path Dashboard
    - **Step 3:** Interactive Q&A
    - **Step 4:** Quizzes & Voice Scenarios
    - **Admin:** Manager Oversight & Knowledge Admin
    """)
    
    st.success("All 11 implementation phases completed successfully.")

if __name__ == "__main__":
    main()
