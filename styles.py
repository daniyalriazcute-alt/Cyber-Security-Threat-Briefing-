import streamlit as st


def load_css(theme="dark"):
    if theme == "dark":
        bg_color = "#121212"
        text_color = "#FFFFFF"
        card_bg = "#1E1E1E"
        card_border = "#333333"
        input_bg = "#2D2D2D"
        login_bg = "#1E1E1E"
        orange_accent = "#FF8C00"
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
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}

        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        div[data-testid="stVerticalBlock"] > div:has(div.login-box) {{
            background: {login_bg};
            border: 1px solid {card_border};
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
            justify-content: center;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            background-color: transparent;
            color: {text_color};
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            color: {orange_accent} !important;
            border-bottom: 2px solid {orange_accent} !important;
        }}

        /* ---- ALL BUTTONS ORANGE (primary + secondary + form submit) ---- */
        div.stButton > button,
        div.stFormSubmitButton > button {{
            background-color: {orange_accent} !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            padding: 8px 20px !important;
        }}
        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {{
            background-color: #E67E00 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(255, 140, 0, 0.4);
        }}

        .company-warning {{
            color: #FF4B4B;
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 15px;
            text-align: center;
            letter-spacing: 0.5px;
        }}

        .agent-card {{
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 10px;
            text-align: center;
        }}

        .agent-avatar {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            margin: 0 auto 12px auto;
            border: 3px solid {orange_accent};
            display: block;
            object-fit: cover;
        }}

        .badge-idle {{
            background-color: #555555;
            color: #FFFFFF;
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            display: inline-block;
        }}
        .badge-writing {{
            background-color: #FF8C00;
            color: #000000;
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            display: inline-block;
        }}
        .badge-done {{
            background-color: #007BFF;
            color: #FFFFFF;
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            display: inline-block;
        }}
        .badge-failed {{
            background-color: #DC3545;
            color: #FFFFFF;
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            display: inline-block;
        }}

        .stTextInput > div > div > input {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {card_border};
            border-radius: 6px;
        }}

        div[data-testid="stSidebar"] {{
            background-color: {card_bg};
            border-right: 1px solid {card_border};
        }}

        p, h1, h2, h3, h4, h5, h6 {{
            color: {text_color};
        }}

        /* Theme toggle row styling */
        .theme-row {{
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 10px;
            margin-bottom: -10px;
        }}
    </style>
    """, unsafe_allow_html=True)
