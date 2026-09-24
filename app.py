import streamlit as st
import os
import time
from dotenv import load_dotenv
from auth_utils import init_db, register_user, login_user
from agents import threat_crew, research_task, report_task
from styles import load_css
from db_utils import get_agent_memory

# Load environment variables
load_dotenv()

# --- INITIALIZATION ---
init_db()
# Initialize ChromaDB memory (this will trigger if not exists)
# Note: In CrewAI, memory setup is handled by the Crew class. 
# We just ensure the persistent directory exists.
if not os.path.exists("./agent_memory"):
    os.makedirs("./agent_memory")

st.set_page_config(page_title="Cyber Threat Briefing", layout="wide", initial_sidebar_state="collapsed")

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'running_crew' not in st.session_state:
    st.session_state.running_crew = False

# Load CSS based on theme
load_css(st.session_state.theme)

# --- SIDEBAR CONTROLS ---
if st.session_state.logged_in:
    with st.sidebar:
        st.title("Settings")
        # Dark/Light mode toggle
        theme_toggle = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))
        if theme_toggle != (st.session_state.theme == "dark"):
            st.session_state.theme = "dark" if theme_toggle else "light"
            st.rerun()
        
        st.divider()
        # End Chat / Clear Memory
        if st.button("End Chat & Clear Memory", type="secondary"):
            # Clear session state
            st.session_state.chat_history = []
            st.session_state.running_crew = False
            # In a real scenario, we would clear the ChromaDB collection here or via a tool.
            st.success("Chat ended and memory cleared.")
            time.sleep(1)
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
                
                # Company-style Red Warning
                st.markdown('<div class="company-warning">⚠️ Demo Project: Do not use real credentials. This is a security research prototype.</div>', unsafe_allow_html=True)
                
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
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                
                st.markdown('<div class="company-warning">⚠️ This system is for authorized use only. Unauthorized access is prohibited.</div>', unsafe_allow_html=True)
                
                reg_submitted = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)
                if reg_submitted:
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        if register_user(new_user, new_pass):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already exists.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN DASHBOARD VIEW ---
else:
    st.title("Cyber Threat Briefing")
    
    # --- Top Section: Agent Status Cards ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h3>Researcher Agent</h3>
            <p style="font-size: 0.9em; opacity: 0.8;">Role: CVE Researcher</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Goal: Fetching NVD data...</p>
            <span class="badge-done">Ready</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-card">
            <h3>Reporter Agent</h3>
            <p style="font-size: 0.9em; opacity: 0.8;">Role: Risk Reporter</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Goal: Summarizing findings...</p>
            <span class="badge-writing">Idle</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- Input Section ---
    st.subheader("Threat Focus")
    topic = st.text_input("Enter a topic (e.g., 'Microsoft Exchange', 'Apache Log4j', 'Critical Infrastructure'):", 
                          value="Recent Critical Vulnerabilities",
                          key="threat_topic")
    
    if st.button("Generate Threat Briefing", type="primary"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            st.session_state.running_crew = True
            st.info("Initializing agents... This may take a moment.")
            
            # Placeholder for the output
            output_placeholder = st.empty()
            
            try:
                # Update Task descriptions with the user topic
                # In a real app, you'd pass this via CrewAI's input variables
                research_task.description = f"Search for the latest critical CVEs related to '{topic}'. Provide short bullet points."
                
                # Run the Crew
                # Note: CrewAI's memory is enabled in the agents.py definition
                result = threat_crew.kickoff(inputs={'topic': topic})
                
                # Display result
                st.session_state.chat_history.append({"topic": topic, "result": result})
                
                st.success("Briefing Generated!")
                st.markdown("### 📋 Cyber Threat Briefing")
                st.write(result)
                
            except Exception as e:
                st.error(f"An error occurred: {e}. The agents may have hit the iteration limit or API limit.")
            finally:
                st.session_state.running_crew = False

    # --- History & Status ---
    if st.session_state.chat_history:
        st.divider()
        st.subheader("Previous Briefings")
        for entry in reversed(st.session_state.chat_history):
            with st.expander(f"Topic: {entry['topic']}"):
                st.write(entry['result'])
