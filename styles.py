import streamlit as st

def load_css(theme="dark"):
    if theme == "dark":
        bg_color = "#121212"
        text_color = "#FFFFFF"
        card_bg = "#1E1E1E"
        card_border = "#333333"
        input_bg = "#2D2D2D"
        login_bg = "#1E1E1E"
        orange_accent = "#FF8C00" # Orange color from the image
    else:
        bg_color = "#F5F7FA"
        text_color = "#333333"
        card_bg = "#FFFFFF"
        card_border = "#E0E0E0"
        input_bg = "#FFFFFF"
        login_bg = "#FFFFFF"
        orange_accent = "#FF8C00"

    st.markdown(f"""
    <style>
        /* Base App styles */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Hide Streamlit default header/footer for cleaner look */
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* Login Box styling */
        div[data-testid="stVerticalBlock"] > div:has(div.login-box) {{
            background: {login_bg};
            border: 1px solid {card_border};
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            max-width: 450px;
            margin: 0 auto;
        }}

        /* Tab styling for Login/Register */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
            justify-content: center;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: {text_color};
        }}
        .stTabs [aria-selected="true"] {{
            color: {orange_accent} !important;
            border-bottom: 2px solid {orange_accent} !important;
        }}
        
        /* Orange Login Button styling */
        div.stButton > button:first-child {{
            background-color: {orange_accent};
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            width: 100%;
        }}
        div.stButton > button:first-child:hover {{
            background-color: #E67E00;
            color: white;
        }}
        
        /* Red Warning Text */
        .company-warning {{
            color: #FF4B4B;
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 15px;
            text-align: center;
            letter-spacing: 0.5px;
        }}

        /* Agent Cards */
        .agent-card {{
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .agent-avatar {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin: 0 auto 10px auto;
            border: 2px solid {orange_accent};
            display: block;
        }}
        
        /* Status Badges */
        .badge-done {{ background-color: #007bff; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }}
        .badge-writing {{ background-color: #FF8C00; color: black; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }}
        
        /* Input Fields */
        .stTextInput > div > div > input {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {card_border};
            border-radius: 5px;
        }}
        
        /* Custom Sidebar Button */
        div[data-testid="stSidebar"] button {{
            width: 100%;
            background-color: transparent;
            border: 1px solid {card_border};
            color: {text_color};
        }}
    </style>
    """, unsafe_allow_html=True)
