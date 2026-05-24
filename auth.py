import os
import hmac
import hashlib
import json
import base64

import streamlit as st

from config import (
    LOGO_PATH, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD_HASH,
    ADMIN_CONFIG_PATH, PALETTE,
)


def _load_admin_config():
    if os.path.exists(ADMIN_CONFIG_PATH):
        try:
            with open(ADMIN_CONFIG_PATH, 'r') as _f:
                return json.load(_f)
        except Exception:
            pass
    return {}


def _save_admin_config(config: dict) -> bool:
    try:
        with open(ADMIN_CONFIG_PATH, 'w') as _f:
            json.dump(config, _f)
        return True
    except Exception:
        return False


def get_active_password_hash() -> str:
    cfg = _load_admin_config()
    if 'password_hash' in cfg:
        return cfg['password_hash']
    try:
        env_hash = st.secrets.get('FAM_ADMIN_PASSWORD_HASH', os.environ.get('FAM_ADMIN_PASSWORD_HASH', ''))
    except Exception:
        env_hash = os.environ.get('FAM_ADMIN_PASSWORD_HASH', '')
    return env_hash if env_hash else DEFAULT_ADMIN_PASSWORD_HASH


def get_secret_value(key, default=''):
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)


def verify_login(username, password):
    admin_username = get_secret_value('FAM_ADMIN_USERNAME', DEFAULT_ADMIN_USERNAME)
    active_hash = get_active_password_hash()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return (
        hmac.compare_digest(username, admin_username)
        and hmac.compare_digest(password_hash, active_hash)
    )


def login_page():
    p = PALETTE
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"]        {{ display: none; }}
    [data-testid="collapsedControl"] {{ display: none; }}
    .stApp {{
        background: linear-gradient(135deg, {p['bg_dark']} 0%, {p['bg']} 55%, {p['secondary']} 100%) !important;
        min-height: 100vh;
    }}
    .block-container {{
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }}
    div[data-testid="stForm"] {{
        background: white !important;
        border-radius: 18px !important;
        padding: 36px 32px 30px !important;
        box-shadow: 0 24px 64px rgba(13,71,161,0.26) !important;
        border: none !important;
    }}
    div[data-testid="stForm"] .stTextInput label {{
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }}
    div[data-testid="stForm"] .stTextInput input {{
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        padding: 10px 14px !important;
        font-size: 0.95rem !important;
        color: #1E293B !important;
        background: #F8FAFC !important;
    }}
    div[data-testid="stForm"] .stTextInput input:focus {{
        border-color: {p['bg']} !important;
        box-shadow: 0 0 0 3px rgba(21,101,192,0.12) !important;
        background: white !important;
    }}
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
        background: linear-gradient(90deg, {p['bg_dark']} 0%, {p['bg']} 100%) !important;
        color: white !important;
        border-radius: 9px !important;
        font-size: 0.97rem !important;
        font-weight: 700 !important;
        padding: 12px !important;
        border: none !important;
        margin-top: 4px !important;
        letter-spacing: 0.02em;
    }}
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {{
        opacity: 0.88 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:6vh"></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.05, 1])

    logo_html = ''
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, 'rb') as _f:
            logo_html = (
                f"<img src='data:image/png;base64,{base64.b64encode(_f.read()).decode()}'"
                f" style='max-width:210px;height:auto;margin-bottom:4px;"
                f"display:block;margin-left:auto;margin-right:auto;'/>"
            )
    else:
        logo_html = "<div style='font-size:2.8rem;text-align:center;margin-bottom:8px;'>📊</div>"

    with col:
        with st.form('login_form'):
            st.markdown(f"""
            {logo_html}
            <h2 style='color:{p["bg_dark"]};font-weight:800;font-size:1.42rem;
                        margin:14px 0 8px;text-align:center;'>
                Dashboard Inventory ATK
            </h2>
            <div style='text-align:center;margin-bottom:20px;'>
                <span style='display:inline-block;padding:4px 14px;border-radius:999px;
                             background:#E8F1FB;color:{p["bg_dark"]};
                             font-size:0.73rem;font-weight:700;'>Internal Analytics System</span>
            </div>
            <hr style='border:none;border-top:1px solid #E2E8F0;margin:0 0 18px;'/>
            """, unsafe_allow_html=True)

            username = st.text_input('Username', placeholder='Masukkan username Anda')
            password = st.text_input('Password', placeholder='Masukkan password Anda', type='password')
            st.markdown('<div style="height:6px"/>', unsafe_allow_html=True)
            submitted = st.form_submit_button('🔐  Login', use_container_width=True)

        if submitted:
            if verify_login(username.strip(), password):
                st.session_state['authenticated'] = True
                st.session_state['admin_username'] = username.strip()
                st.rerun()
            else:
                st.error('Login gagal. Username atau password tidak sesuai.')


def require_login():
    if st.session_state.get('authenticated'):
        return True
    login_page()
    return False
