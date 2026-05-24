import os
import base64

import streamlit as st

from config import LOGO_PATH, PALETTE
from style import set_page_style
from auth import require_login
from data.loader import load_and_validate, show_upload_error
from data.processor import prepare_data, compute_model1, compute_model2, compute_model3
from views.overview import page_overview
from views.model1 import page_model1
from views.model2 import page_model2
from views.model3 import page_model3
from views.export import page_export
from views.settings import page_update_password


set_page_style()
if not require_login():
    st.stop()

# Paksa sidebar tampil setelah login
st.markdown("""
<style>
[data-testid="stSidebar"]       { display: flex !important; }
[data-testid="stSidebar"] > div { display: flex !important; flex-direction: column; }
</style>
""", unsafe_allow_html=True)

# Sidebar logo
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, 'rb') as _lf:
        _logo_b64 = base64.b64encode(_lf.read()).decode()
    _logo_tag = (
        f"<img src='data:image/png;base64,{_logo_b64}' "
        f"style='height:42px;width:auto;object-fit:contain;border-radius:4px;flex-shrink:0;'/>"
    )
else:
    _logo_tag = (
        f"<div style='background:white;border-radius:8px;width:46px;height:42px;"
        f"display:flex;align-items:center;justify-content:center;flex-shrink:0;"
        f"font-weight:900;color:{PALETTE['bg_dark']};font-size:1rem;'>"
        f"R<span style='color:{PALETTE['accent']};'>A</span></div>"
    )

st.sidebar.markdown(f"""
<div style='background:rgba(255,255,255,0.11);padding:14px 14px 13px;
            border-bottom:1px solid rgba(255,255,255,0.18);margin-bottom:4px;'>
    <div style='display:flex;align-items:center;gap:11px;'>
        {_logo_tag}
        <div style='min-width:0;'>
            <p style='color:white;font-weight:800;font-size:0.93rem;margin:0;line-height:1.2;'>Bank Raya Indonesia</p>
            <p style='color:rgba(255,255,255,0.68);font-size:0.70rem;margin:2px 0 0;'>Sistem Analitik Inventory ATK</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Data & Filter section
st.sidebar.markdown("""
<p style='color:rgba(255,255,255,0.40);font-size:0.68rem;font-weight:700;
          letter-spacing:0.09em;margin:10px 0 6px 4px;'>DATA & FILTER</p>
""", unsafe_allow_html=True)

uploaded = st.sidebar.file_uploader('Upload Dataset', type=['xlsx', 'xls'])

if uploaded is not None:
    raw_df, upload_error = load_and_validate(uploaded)
    if upload_error:
        fdf = None
    else:
        prepared_df = prepare_data(raw_df)
        years    = sorted(prepared_df['Tahun'].dropna().unique().astype(int).tolist())
        sel_year = st.sidebar.selectbox('Tahun', ['Semua Tahun'] + [str(y) for y in years])
        fdf = prepared_df.copy()
        if sel_year != 'Semua Tahun':
            fdf = fdf[fdf['Tahun'] == int(sel_year)]
else:
    upload_error = None
    fdf = None

# Navigation
st.sidebar.markdown('---')
st.sidebar.markdown("""
<p style='color:rgba(255,255,255,0.40);font-size:0.68rem;font-weight:700;
          letter-spacing:0.09em;margin:0 0 6px 4px;'>NAVIGASI DASHBOARD</p>
""", unsafe_allow_html=True)

nav = st.sidebar.radio('', [
    'Overview',
    'Model 1 - Segmentasi Konsumsi Divisi',
    'Model 2 - Segmentasi Pergerakan Produk ATK',
    'Model 3 - Segmentasi Prioritas Divisi-Item',
    'Export & Laporan',
], label_visibility='collapsed')

st.sidebar.markdown(f"""
<div style='margin-top:80px;text-align:center;padding:18px 12px 10px;
            border-top:1px solid rgba(255,255,255,0.16);'>
    <p style='color:rgba(255,255,255,0.58);font-size:0.70rem;margin:0;'>
        © 2025 Sistem Analitik ATK
    </p>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button('Update Password', use_container_width=True):
    st.session_state['show_update_pw'] = True
    st.session_state['_pw_entry_nav'] = nav
    st.rerun()
if st.sidebar.button('Logout', use_container_width=True):
    st.session_state.clear()
    st.rerun()

# Halaman Update Password
if st.session_state.get('show_update_pw', False):
    if nav != st.session_state.get('_pw_entry_nav', nav):
        st.session_state['show_update_pw'] = False
        st.session_state.pop('_pw_entry_nav', None)
    else:
        page_update_password()
        st.stop()

# Tidak ada file / file tidak valid
if fdf is None:
    if upload_error:
        show_upload_error(upload_error)
    else:
        st.markdown(f"""
        <div style='text-align:center;padding:100px 20px;'>
            <span style='font-size:4.5rem;'>📂</span>
            <h3 style='color:{PALETTE["bg"]};margin-top:16px;'>Unggah File Excel untuk Memulai</h3>
            <p style='color:#999;font-size:0.95rem;'>
                Gunakan panel sidebar di sebelah kiri untuk mengunggah file Excel ATK Anda.
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# Hitung model
load_area = st.empty()
load_area.markdown(f"""
<div class='loading-wrap'>
    <div class='loading-dot'></div>
    <div style='color:{PALETTE["text_dark"]};font-weight:650;'>Memproses data dan membangun visualisasi...</div>
</div>
""", unsafe_allow_html=True)
with st.spinner('Memproses data dan membangun visualisasi...'):
    m1, m1_res = compute_model1(fdf)
    m2, m2_res = compute_model2(fdf)
    m3, m3_res = compute_model3(fdf)
load_area.empty()

# Routing halaman
if 'Overview' in nav:
    page_overview(fdf, m1, m2, m3)
elif 'Model 1' in nav:
    page_model1(fdf, m1, m1_res)
elif 'Model 2' in nav:
    page_model2(fdf, m2, m2_res)
elif 'Model 3' in nav:
    page_model3(fdf, m3, m3_res)
else:
    page_export(fdf, m1, m2, m3, m1_res, m2_res, m3_res)
