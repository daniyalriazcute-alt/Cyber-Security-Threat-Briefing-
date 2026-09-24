# --- SQLITE3 PATCH (must be first, before any other imports) ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ----------------------------------------------------------------

import streamlit as st
import os
import time
import base64
import traceback
import pandas as pd
from dotenv import load_dotenv
from auth_utils import init_db, register_user, login_user
from agents import get_crew
from styles import load_css

load_dotenv()
init_db()
st.set_page_config(
    page_title="Cyber Threat Briefing",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# IMAGE LOADER (base64)
# ============================================================
def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{data}"
    except FileNotFoundError:
        return ""


VEGA_IMG = img_to_base64("./assets/vega.png")
ORION_IMG = img_to_base64("./assets/orion.png")


# ============================================================
# BRIEFING PARSER
# ============================================================
def parse_briefing(text):
    """Parse the 5-line schema per CVE into a DataFrame."""
    rows = []
    current = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("CVE ID:"):
            if current:
                rows.append(current)
            current = {"CVE ID": line.replace("CVE ID:", "").strip()}
        elif ":" in line and current:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if key and val:
                current[key] = val
    if current:
        rows.append(current)
    return pd.DataFrame(rows)


# ============================================================
# SESSION STATE
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_status' not in st.session_state:
    st.session_state.agent_status = {"vega": "Idle", "orion": "Idle"}
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'last_usage' not in st.session_state:
    st.session_state.last_usage = ""

load_css(st.session_state.theme)


# ============================================================
# LOGIN / REGISTRATION VIEW
# ============================================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Log in")
            with st.form("login_form"):
                username = st.text_input(
                    "Username", placeholder="Enter your username"
                )
                password = st.text_input(
                    "Password", type="password", placeholder="Enter your password"
                )
                st.markdown(
                    '<div class="company-warning">'
                    '⚠️ Demo Project: Do not use real credentials. '
                    'This is a security research prototype.'
                    '</div>',
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
                    '<div class="company-warning">'
                    '⚠️ This system is for authorized use only. '
                    'Unauthorized access is prohibited.'
                    '</div>',
                    unsafe_allow_html=True
                )
                reg_submitted = st.form_submit_button(
                    "CREATE ACCOUNT", use_container_width=True
                )
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


# ============================================================
# MAIN DASHBOARD VIEW
# ============================================================
else:
    # --- Header with Theme Toggle ---
    title_col, toggle_col = st.columns([4, 1])
    with title_col:
        st.title("Cyber Threat Briefing")
    with toggle_col:
        st.write("")
        theme_on = st.toggle(
            "🌙 Dark Mode",
            value=(st.session_state.theme == "dark")
        )
        if theme_on != (st.session_state.theme == "dark"):
            st.session_state.theme = "dark" if theme_on else "light"
            st.rerun()

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

    # --- Threat Focus Input ---
    st.subheader("Threat Focus")
    topic = st.text_input(
        "Enter a topic (e.g., 'Microsoft Exchange', 'Apache Log4j'):",
        value="Recent Critical Vulnerabilities",
        key="threat_topic"
    )

    if st.button("Generate Threat Briefing"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            st.session_state.agent_status = {"vega": "Writing", "orion": "Idle"}
            st.rerun()

    # --- Run the Crew ---
    if st.session_state.agent_status['vega'] == "Writing":
        topic_value = st.session_state.get(
            'threat_topic', 'Recent Critical Vulnerabilities'
        )
        try:
            with st.spinner("Agents are collaborating..."):
                crew = get_crew()
                result = crew.kickoff(inputs={'topic': topic_value})

            raw = str(result.raw) if hasattr(result, 'raw') else str(result)
            final_text = "\n".join(
                line for line in raw.splitlines() if line.strip()
            )

            if hasattr(result, 'token_usage') and result.token_usage:
                tu = result.token_usage
                st.session_state.last_usage = (
                    f"{tu.total_tokens} tokens "
                    f"({tu.prompt_tokens} prompt + "
                    f"{tu.completion_tokens} output)"
                )

            st.session_state.chat_history.append({
                "topic": topic_value,
                "result": final_text
            })
            st.session_state.agent_status = {"vega": "Done", "orion": "Done"}
            st.success("Briefing Generated!")

        except Exception as e:
            st.error("❌ Agent execution failed.")
            st.code(traceback.format_exc(), language="python")
            st.session_state.agent_status = {"vega": "Failed", "orion": "Failed"}
        finally:
            time.sleep(0.5)
            st.rerun()

    # --- Token Usage ---
    if st.session_state.last_usage:
        st.caption(f"📊 Last run: {st.session_state.last_usage}")

    # --- History ---
    if st.session_state.chat_history:
        st.divider()
        st.subheader("Threat Briefing History")
        for entry in reversed(st.session_state.chat_history):
            with st.expander(f"Topic: {entry['topic']}", expanded=True):
                df = parse_briefing(entry['result'])
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.text(entry['result'])

    # --- End Chat & Logout ---
    st.divider()
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("End Chat & Clear Memory", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.agent_status = {"vega": "Idle", "orion": "Idle"}
            st.session_state.last_usage = ""
            st.success("Chat ended and memory cleared.")
            time.sleep(1)
            st.rerun()
    with btn_col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.chat_history = []
            st.session_state.username = ""
            st.session_state.agent_status = {"vega": "Idle", "orion": "Idle"}
            st.session_state.last_usage = ""
            st.rerun()
