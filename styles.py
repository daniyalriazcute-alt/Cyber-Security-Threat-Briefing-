import streamlit as st

def load_css(theme="dark"):
    """
    Injects professional CSS for Dark/Light mode and a company-style warning.
    """
    if theme == "dark":
        bg_color = "#1E1E1E"
        text_color = "#FFFFFF"
        card_bg = "#2D2D2D"
        card_border = "#444"
        login_bg = "linear-gradient(135deg, #2c3e50, #000000)"
    else:
        bg_color = "#F5F7FA"
        text_color = "#333333"
        card_bg = "#FFFFFF"
        card_border = "#E0E0E0"
        login_bg = "linear-gradient(135deg, #e0eafc, #cfdef3)"

    st.markdown(f"""
    <style>
        /* Base styles */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Login Box styling */
        .login-box {{
            background: {login_bg};
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }}
        
        /* The RED warning text (company style) */
        .company-warning {{
            color: #FF4B4B;
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 5px;
            margin-bottom: 15px;
            text-align: center;
            letter-spacing: 0.5px;
        }}

        /* Agent Card styling */
        .agent-card {{
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        /* Status Badges */
        .badge-done {{ background-color: #007bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }}
        .badge-writing {{ background-color: #ffc107; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }}
        
        /* Custom Input styling */
        .stTextInput > div > div > input {{
            background-color: {card_bg};
            color: {text_color};
            border: 1px solid {card_border};
        }}
    </style>
    """, unsafe_allow_html=True)
