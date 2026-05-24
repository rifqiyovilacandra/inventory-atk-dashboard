import streamlit as st

from config import PALETTE, LABEL_COLORS


def section_header(title, subtitle=''):
    sub = f"<p class='page-subtitle'>{subtitle}</p>" if subtitle else ''
    st.markdown(f"""
    <div class='page-title'>
        <h3>{title}</h3>
        {sub}
    </div>
    """, unsafe_allow_html=True)


def loading_card(text='Memproses data dan membangun visualisasi...'):
    st.markdown(f"""
    <div class='loading-wrap'>
        <div class='loading-dot'></div>
        <div style='color:{PALETTE["text_dark"]};font-weight:650;'>{text}</div>
    </div>
    """, unsafe_allow_html=True)


def label_color(label, fallback_index=0):
    return LABEL_COLORS.get(
        str(label),
        PALETTE['cluster_colors'][fallback_index % len(PALETTE['cluster_colors'])]
    )


def filter_dataframe(df, key):
    query = st.text_input(
        'Cari data',
        placeholder='Ketik divisi, item, cluster, atau label...',
        key=key,
    )
    if not query:
        return df
    q = query.strip().lower()
    if not q:
        return df
    mask = df.astype(str).apply(lambda col: col.str.lower().str.contains(q, na=False)).any(axis=1)
    return df[mask]
