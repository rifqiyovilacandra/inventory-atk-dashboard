import streamlit as st

from config import PALETTE


def set_page_style():
    st.set_page_config(
        page_title='Sistem Analitik Inventory ATK',
        page_icon=':bar_chart:',
        layout='wide',
        initial_sidebar_state='expanded',
    )
    p = PALETTE
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {p['surface']};
        color: {p['text_dark']};
        font-family: "Segoe UI", Inter, Arial, sans-serif;
    }}
    .block-container {{
        padding-top: 1.3rem;
        padding-bottom: 2rem;
        max-width: 1480px;
    }}
    [data-testid="stHeader"] {{ display: none !important; }}
    h1,h2,h3,h4,h5,h6 {{ color: {p['bg_dark']} !important; letter-spacing: 0; }}
    p, span, label, div {{ letter-spacing: 0; }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {p['bg_dark']} 0%, {p['bg']} 62%, {p['accent']} 130%) !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, {p['bg_dark']} 0%, {p['bg']} 62%, {p['accent']} 130%) !important;
        padding-top: 0 !important;
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
    [data-testid="stSidebar"] .stRadio label *,
    [data-testid="stSidebar"] .stFileUploader * {{
        color: rgba(255,255,255,0.92) !important;
        text-shadow: none !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background-color: rgba(255,255,255,0.14) !important;
        border-color: rgba(255,255,255,0.28) !important;
        color: white !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] div {{
        color: white !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        fill: rgba(255,255,255,0.78) !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stFileUploader label,
    [data-testid="stSidebar"] label {{
        font-size: 0.74rem !important;
        color: rgba(255,255,255,0.76) !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"] label {{
        display: flex !important;
        align-items: center !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        color: rgba(255,255,255,0.75) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        cursor: pointer !important;
        margin: 1px 0 !important;
        transition: background 0.15s;
        white-space: normal !important;
        line-height: 1.25 !important;
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"] label:hover {{
        background-color: rgba(255,255,255,0.18) !important;
        color: white !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"] label > div:first-child {{
        display: none !important;
    }}
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {{
        display: none !important;
    }}
    .stButton>button {{
        background-color: {p['accent']}; color: white;
        border: none; border-radius: 8px; font-weight: 600; padding: 8px 20px;
    }}
    .stButton>button:hover {{ background-color: {p['accent_light']}; color: white; }}
    [data-testid="stFormSubmitButton"] button {{
        background-color: {p['accent']} !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; padding: 8px 20px !important;
    }}
    [data-testid="stFormSubmitButton"] button:hover {{
        background-color: #E65100 !important; color: white !important;
    }}
    .stDownloadButton > button {{
        background-color: {p['bg']}; color: white;
        border: none; border-radius: 8px; font-weight: 600; padding: 8px 20px;
        transition: none !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: {p['bg']} !important; color: white !important;
        border: none !important; box-shadow: none !important; transform: none !important;
    }}
    div[data-testid="metric-container"] {{
        background: white;
        border: 1px solid {p['border']};
        border-top: 3px solid {p['bg']};
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        min-height: 122px;
    }}
    div[data-testid="metric-container"] *,
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] p,
    div[data-testid="metric-container"] span {{
        color: {p['text_dark']} !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }}
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] {{
        color: #334155 !important; font-size: 0.82rem !important; font-weight: 700;
    }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
        color: {p['bg_dark']} !important; font-size: 1.75rem !important; font-weight: 700;
    }}
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"],
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] * {{
        color: #15803D !important; font-size: 0.78rem !important; font-weight: 700;
    }}
    [data-testid="stTable"] *,
    [data-testid="stDataFrame"] *,
    div[data-testid="stAlert"] *,
    div[data-testid="stMarkdownContainer"] p {{
        color: {p['text_dark']};
    }}
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {p['bg']}; border-radius: 10px 10px 0 0; padding: 4px 6px 0; gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: rgba(255,255,255,0.70); font-weight: 600; border-radius: 8px 8px 0 0; padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {p['accent']} !important; color: white !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        background: white; border-radius: 0 0 12px 12px;
        padding: 24px; border: 1px solid {p['border']}; border-top: none;
    }}
    div[data-testid="stPlotlyChart"] {{
        background: white;
        border: 1px solid {p['border']};
        border-radius: 8px;
        padding: 10px 10px 2px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.045);
    }}
    div[data-testid="stPlotlyChart"] .main-svg text {{
        fill: {p['text_dark']} !important;
    }}
    div[data-testid="stPlotlyChart"] .legendtext,
    div[data-testid="stPlotlyChart"] .xtick text,
    div[data-testid="stPlotlyChart"] .ytick text {{
        fill: {p['text_dark']} !important;
    }}
    div[data-testid="stPlotlyChart"] .sankey text {{
        fill: {p['text_dark']} !important;
        font-family: Arial, sans-serif !important;
        font-size: 13px !important;
        shape-rendering: crispEdges;
        text-rendering: optimizeLegibility;
    }}
    .page-title {{
        background: white;
        border: 1px solid {p['border']};
        border-left: 4px solid {p['accent']};
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.045);
    }}
    .page-title p {{
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 700;
        margin: 0 0 4px;
        text-transform: uppercase;
    }}
    .page-title .page-subtitle {{
        color: #64748B;
        font-size: 0.88rem;
        font-weight: 500;
        margin: 6px 0 0;
        text-transform: none;
    }}
    .page-title h2, .page-title h3 {{
        color: {p['bg_dark']} !important;
        margin: 0;
        font-weight: 750;
    }}
    .loading-wrap {{
        display:flex;
        align-items:center;
        gap:12px;
        background:white;
        border:1px solid {p['border']};
        border-radius:8px;
        padding:14px 16px;
        margin:12px 0;
    }}
    .loading-dot {{
        width:18px;
        height:18px;
        border-radius:999px;
        border:3px solid #E2E8F0;
        border-top-color:{p['accent']};
        animation: spin 0.8s linear infinite;
    }}
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] button[kind="header"],
    button[data-testid="stBaseButton-headerNoPadding"] {{
        display: none !important;
    }}
    .login-wrap {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, {p['bg_dark']} 0%, {p['bg']} 55%, {p['secondary']} 100%);
        padding: 2rem 1rem;
    }}
    .login-box {{
        background: white;
        border-radius: 18px;
        padding: 40px 38px 36px;
        width: 100%;
        max-width: 440px;
        box-shadow: 0 24px 64px rgba(13,71,161,0.28);
        text-align: center;
    }}
    .login-box h2 {{
        color: {p['bg_dark']} !important;
        font-size: 1.45rem;
        font-weight: 800;
        margin: 16px 0 6px;
    }}
    .login-box p {{
        color: #64748B !important;
        font-size: 0.88rem;
        margin: 0 0 14px;
        line-height: 1.5;
    }}
    .login-badge {{
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        background: #E8F1FB;
        color: {p['bg_dark']} !important;
        font-size: 0.73rem;
        font-weight: 700;
        margin-top: 12px;
    }}
    .login-card {{
        background: white;
        border-radius: 14px;
        box-shadow: 0 8px 32px rgba(13,71,161,0.14);
        padding: 32px 28px;
        text-align: center;
        margin: 28px auto 14px;
        max-width: 460px;
    }}
    .login-card h2 {{
        color: {p['bg_dark']} !important;
        margin: 14px 0 6px;
        font-weight: 800;
    }}
    .login-card p {{
        color: #64748B !important;
        margin: 0;
        font-size: 0.92rem;
    }}
    .stDataFrame {{ border-radius: 10px; overflow: hidden; }}
    div[data-testid="stAlert"] {{ border-radius: 10px; }}
    hr {{ border-color: {p['border']}; margin: 12px 0; }}
    @media (max-width: 900px) {{
        .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        div[data-testid="metric-container"] {{ min-height: auto; }}
    }}
    </style>
    """, unsafe_allow_html=True)
