import hashlib
import hmac

import streamlit as st

from config import PALETTE, ADMIN_CONFIG_PATH
from auth import get_active_password_hash, _load_admin_config, _save_admin_config
from ui import section_header


def page_update_password():
    p = PALETTE
    section_header('Update Password', 'Ganti password akun administrator')

    if st.button('← Kembali ke Dashboard'):
        st.session_state['show_update_pw'] = False
        st.rerun()

    if st.session_state.pop('pw_updated', False):
        st.success('Password berhasil diperbarui dan disimpan.')

    col_center, _ = st.columns([1, 1])
    with col_center:
        with st.form('form_update_password'):
            st.markdown(f"""
            <p style='color:{p["bg_dark"]};font-weight:700;font-size:1rem;margin-bottom:4px;'>
                Ubah Password Admin
            </p>
            <p style='color:#64748B;font-size:0.84rem;margin-bottom:16px;'>
                Password baru akan langsung berlaku dan tersimpan permanen.
            </p>
            """, unsafe_allow_html=True)

            current_pw = st.text_input('Password Saat Ini', type='password',
                                       placeholder='Masukkan password saat ini')
            new_pw     = st.text_input('Password Baru', type='password',
                                       placeholder='Minimal 8 karakter')
            confirm_pw = st.text_input('Konfirmasi Password Baru', type='password',
                                       placeholder='Ulangi password baru')

            submitted = st.form_submit_button('Simpan Password', use_container_width=True)

    if submitted:
        active_hash  = get_active_password_hash()
        current_hash = hashlib.sha256(current_pw.encode()).hexdigest()

        if not hmac.compare_digest(current_hash, active_hash):
            st.error('Password saat ini tidak sesuai.')
        elif len(new_pw) < 8:
            st.warning('Password baru minimal 8 karakter.')
        elif new_pw != confirm_pw:
            st.warning('Konfirmasi password tidak cocok.')
        else:
            new_hash = hashlib.sha256(new_pw.encode()).hexdigest()
            cfg = _load_admin_config()
            cfg['password_hash'] = new_hash
            if _save_admin_config(cfg):
                st.session_state['pw_updated'] = True
                st.rerun()
            else:
                st.error(f'Gagal menyimpan ke file. Pastikan folder dapat ditulis: {ADMIN_CONFIG_PATH}')
