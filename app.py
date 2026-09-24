import streamlit as st
import os
import time
from dotenv import load_dotenv
from auth_utils import init_db, register_user, login_user
from agents import threat_crew, research_task, report_task
from styles import load_css

# Load environment variables
load_dotenv()

# --- INITIALIZATION ---
init_db()
st.set_page_config(page_title="Cyber Threat Briefing", layout="wide", initial_sidebar_state="collapsed")

# --- IMAGE PATHS ---
VEGA_IMG = "./assets/vega.png"
ORION_IMG = "./assets/orion.png"

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'running_crew' not in st.session_state:
    st.session_state.running_crew = False
if 'agent_status' not in st.session_state:
    st.session_state.agent_status = {"vega": "Idle", "orion": "Idle"}
if 'username' not in st.session_state:
    st.session_state.username = ""

# Load CSS based on theme
load_css(st.session_state.theme)

# --- SIDEBAR (only visible when logged in) ---
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}")
        st.divider()

        theme_toggle = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))
        if theme_toggle != (st.session_state.theme == "dark"):
            st.session_state.theme = "dark" if theme_toggle else "light"
            st.rerun()

        st.divider()

        if st.button("Logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.chat_history = []
            st.session_state.username = ""
            st.session_state.agent_status = {"vega": "Idle", "orion": "Idle"}
            st.rerun()

# --- LOGIN / REGISTRATION VIEW ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Log in")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")

                st.markdown(
                    '<div class="company-warning">⚠️ Demo Project: Do not use real credentials. This is a security research prototype.</div>',
                    unsafe_allow_html=True
                )

                submitted = st.form_submit_button("LOGIN", use_container_width=True)
                if submitted:
                    if login_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

        with tab2:
            st.subheader("Register")
            with st.form("register_form"):
                new_user = st.text_input("New Username")
                new_email = st.text_input("Email Address")
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")

                st.markdown(
                    '<div class="company-warning">⚠️ This system is for authorized use only. Unauthorized access is prohibited.</div>',
                    unsafe_allow_html=True
                )

                reg_submitted = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)
                if reg_submitted:
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif "@" not in new_email:
                        st.error("Please enter a valid email address.")
                    else:
                        if register_user(new_user, new_email, new_pass):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already exists.")

        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN DASHBOARD VIEW ---
else:
    st.title("Cyber Threat Briefing")

    # --- Agent Status Cards ---
    col1, col2 = st.columns(2)

    with col1:
        vega_status = st.session_state.agent_status['vega'].lower()
        st.markdown(f"""
        <div class="agent-card">
            <img src="{VEGA_IMG}" class="agent-avatar">
            <h3>Vega</h3>
            <p style="font-size: 0.9em; opacity: 0.8;">CVE Researcher</p>
            <span class="badge-{vega_status}">{st.session_state.agent_status['vega']}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        orion_status = st.session_state.agent_status['orion'].lower()
        st.markdown(f"""
        <div class="agent-card">
            <img src="{ORION_IMG}" class="agent-avatar">
            <h3>Orion</h3>
            <p style="font-size: 0.9em; opacity: 0.8;">Risk Reporter</p>
            <span class="badge-{orion_status}">{st.session_state.agent_status['orion']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- Input Section ---
    st.subheader("Threat Focus")
    topic = st.text_input(
        "Enter a topic (e.g., 'Microsoft Exchange', 'Apache Log4j'):",
        value="Recent Critical Vulnerabilities",
        key="threat_topic"
    )

    if st.button("Generate Threat Briefing", type="primary"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            st.session_state.agent_status = {"vega": "Writing", "orion": "Idle"}
            st.rerun()

    # --- Run the crew if status is Writing ---
    if st.session_state.agent_status['vega'] == "Writing":
        topic_value = st.session_state.get('threat_topic', 'Recent Critical Vulnerabilities')
        try:
            with st.spinner("Agents are collaborating..."):
                research_task.description = (
                    f"Search for the latest critical CVEs related to '{topic_value}'. "
                    f"Provide short bullet points."
                )
                result = threat_crew.kickoff(inputs={'topic': topic_value})

                st.session_state.chat_history.append({"topic": topic_value, "result": result})
                st.session_state.agent_status = {"vega": "Done", "orion": "Done"}
                st.success("Briefing Generated!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.agent_status = {"vega": "Failed", "orion": "Failed"}
        finally:
            st.rerun()

    # --- History ---
    if st.session_state.chat_history:
        st.divider()
        st.subheader("Threat Briefing History")
        for entry in reversed(st.session_state.chat_history):
            with st.expander(f"Topic: {entry['topic']}"):
                st.write(entry['result'])

    # --- End Chat Button ---
    st.divider()
    if st.button("End Chat & Clear Memory", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.agent_status = {"vega": "Idle", "orion": "Idle"}
        st.success("Chat ended and memory cleared.")
        time.sleep(1)
        st.rerun()
