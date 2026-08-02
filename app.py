import sys 
import streamlit as st
from socratic_tutor import process_student_turn, TutorState

st.write("**Python executable:**", sys.executable)
st.write("**Python version:**", sys.version)

st.set_page_config(page_title="Math Tutor", layout="wide")
st.title("Multi-Agent Math Tutor")

# ====================== SESSION STATE ======================
if "state" not in st.session_state:
    st.session_state.state: TutorState = {
        "student_input": "",
        "student_emotion": "neutral",
        "progress": "beginning",
        "known_mistake": None,
        "history": [],
        "orchestrator_instruction": "",
        "affective_suggestion": "",
        "final_response": "",
        "problem_solved": False,
        "reflection_count": 0,
        "next_agent": None,
        "current_problem": None,
        "original_problem": None,
        "debug_logs": [],
    }

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("System Status")

    # Affective State (Always Visible)
    st.subheader("Affective State")
    emotion = st.session_state.state.get("student_emotion", "neutral")
    suggestion = st.session_state.state.get("affective_suggestion", "")
    
    st.markdown(f"**Emotion:** `{emotion}`")
    if suggestion:
        st.info(suggestion)

    # Debug Mode Toggle
    st.session_state.debug_mode = st.toggle("Debug Mode", value=st.session_state.debug_mode)

    # How to Interact (Hidden behind button)
    with st.expander("How to interact"):
        st.markdown("""
        **To start a new problem**, use phrases like:
        - "I need help with..."
        - "How do I solve..."
        - "Solve the following..."
        """)

    # Current Problem
    if st.session_state.state.get("current_problem"):
        st.subheader("Current Problem")
        st.write(st.session_state.state["current_problem"])

# ====================== MAIN CHAT ======================
st.subheader("Conversation")

# Display chat history
for msg in st.session_state.state.get("history", []):
    if msg.startswith("Student:"):
        with st.chat_message("user"):
            st.write(msg.replace("Student: ", ""))
    else:
        with st.chat_message("assistant"):
            st.write(msg.replace("System: ", "").replace("System (Meta): ", ""))

# Debug logs (only shown when debug mode is on)
if st.session_state.debug_mode:
    with st.expander("Debug Logs", expanded=True):
        for log in st.session_state.state.get("debug_logs", []):
            st.code(log, language="text")

# ====================== USER INPUT ======================
user_input = st.chat_input("Type your message here...")

if user_input:
    with st.spinner("Thinking..."):
        try:
            result = process_student_turn(st.session_state.state, user_input)
            st.session_state.state.update(result)
        except Exception as e:
            st.error(f"Backend error: {e}")
            st.exception(e)   # This will show the full traceback
    st.rerun()