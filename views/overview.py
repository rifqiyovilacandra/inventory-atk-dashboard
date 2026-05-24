import streamlit as st

from config import PALETTE
from charts.plots import (
    chart_donut, chart_bar_top, chart_trend, chart_scatter, chart_heatmap,
)
from exports.excel import to_excel


def page_overview(df, m1, m2, m3):
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric('Total Transaksi',         f'{len(df):,}',                  'Transaksi')
    with c2: st.metric('Total Divisi',            f'{df["Divisi"].nunique():,}',    'Divisi')
    with c3: st.metric('Total Jenis ATK',         f'{df["Jenis_ATK"].nunique():,}', 'Jenis ATK')
    with c4: st.metric('Total Permintaan (Unit)', f'{df["Jumlah"].sum():,.0f}',     'Unit')
    with c5: st.metric('Rata-rata per Transaksi', f'{df["Jumlah"].mean():.2f}',     'Unit')

    st.markdown('<div style="height:10px"/>', unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        if m1 is not None:
            st.plotly_chart(chart_donut(m1, 'Label', 'Distribusi Cluster — Model 1 (Divisi)'),
                            use_container_width=True)
        else:
            st.info('Data Model 1 tidak cukup.')
    with r1c2:
        top_div = df.groupby('Divisi')['Jumlah'].sum().reset_index(name='Total_Volume')
        st.plotly_chart(
            chart_bar_top(top_div, 'Total_Volume', 'Divisi', 'Top 10 Divisi — Berdasarkan Total Volume'),
            use_container_width=True,
        )

    r1c3, r1c4 = st.columns(2)
    with r1c3:
        top_atk = df.groupby('Jenis_ATK').size().reset_index(name='Frekuensi')
        st.plotly_chart(
            chart_bar_top(top_atk, 'Frekuensi', 'Jenis_ATK', 'Top 10 Item ATK — Berdasarkan Frekuensi'),
            use_container_width=True,
        )
    with r1c4:
        st.plotly_chart(chart_trend(df, 'Tren Permintaan (Total Unit)'), use_container_width=True)

    st.markdown('<div style="height:4px"/>', unsafe_allow_html=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        if m1 is not None:
            st.plotly_chart(
                chart_scatter(m1, 'Volume', 'Frekuensi', 'Label',
                              'Model 1 — Segmentasi Divisi (Volume vs Frekuensi)'),
                use_container_width=True,
            )
        else:
            st.info('Data Model 1 tidak cukup.')
    with r2c2:
        if m2 is not None:
            st.plotly_chart(
                chart_scatter(m2, 'Total_Jumlah', 'Frekuensi', 'Label',
                              'Model 2 — Segmentasi Produk ATK (Frekuensi vs Total Unit)'),
                use_container_width=True,
            )
        else:
            st.info('Data Model 2 tidak cukup.')

    if m3 is not None:
        st.plotly_chart(
            chart_heatmap(m3, 'Model 3 — Heatmap Prioritas Divisi-Item (Skor Ketergantungan)'),
            use_container_width=True,
        )
    else:
        st.info('Data Model 3 tidak cukup.')

    st.markdown('<div style="height:4px"/>', unsafe_allow_html=True)

    tc, ec = st.columns([7, 3])
    with tc:
        st.markdown(f"<h4 style='color:{PALETTE['bg_dark']};margin-bottom:8px;'>Tabel Ringkasan Hasil Clustering</h4>",
                    unsafe_allow_html=True)
        tabs = st.tabs(['Model 1 - Divisi', 'Model 2 - Produk', 'Model 3 - Divisi-Item'])
        with tabs[0]:
            if m1 is not None:
                st.dataframe(
                    m1.groupby(['Cluster', 'Label']).agg(
                        Jumlah_n=('Divisi', 'count'),
                        Rata_Volume=('Volume', 'mean'),
                        Rata_Frekuensi=('Frekuensi', 'mean'),
                    ).reset_index().round(1), use_container_width=True)
            else:
                st.info('Model 1 tidak dapat dijalankan dengan data ini.')
        with tabs[1]:
            if m2 is not None:
                st.dataframe(
                    m2.groupby(['Cluster', 'Label']).agg(
                        Jumlah_n=('Jenis_ATK', 'count'),
                        Rata_Frekuensi=('Frekuensi', 'mean'),
                        Rata_Total_Jumlah=('Total_Jumlah', 'mean'),
                        Rata_per_Req=('Rata_per_Req', 'mean'),
                        Rata_Jumlah_Divisi=('Jumlah_Divisi', 'mean'),
                    ).reset_index().round(1), use_container_width=True)
            else:
                st.info('Model 2 tidak dapat dijalankan dengan data ini.')
        with tabs[2]:
            if m3 is not None:
                st.dataframe(
                    m3.groupby(['Cluster', 'Label']).agg(
                        Jumlah_n=('Divisi', 'count'),
                        Rata_Skor=('Skor_Ketergantungan', 'mean'),
                        Rata_Frekuensi=('Frekuensi', 'mean'),
                    ).reset_index().round(4), use_container_width=True)
            else:
                st.info('Model 3 tidak dapat dijalankan dengan data ini.')

    with ec:
        st.markdown(f"<h4 style='color:{PALETTE['bg_dark']};margin-bottom:8px;'>Export & Laporan</h4>",
                    unsafe_allow_html=True)
        st.write('Pilih format laporan yang ingin diunduh')

        sheets = {}
        if m1 is not None:
            sheets['1-Segmentasi Konsumsi Divisi'] = m1[['Divisi', 'Volume', 'Frekuensi', 'Cluster', 'Label']]
        if m2 is not None:
            sheets['2-Segmentasi Pergerakan ATK'] = m2[['Jenis_ATK', 'Total_Jumlah', 'Frekuensi', 'Cluster', 'Label']]
        if m3 is not None:
            sheets['3-Prioritas Divisi-Item'] = m3[['Divisi', 'Jenis_ATK', 'Total_Jumlah',
                                                     'Frekuensi', 'Skor_Ketergantungan', 'Cluster', 'Label']]
        if sheets:
            st.download_button(
                label='📥  Export ke Excel (.xlsx)',
                data=to_excel(sheets),
                file_name='segmentasi_atk.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True,
            )
        st.markdown('<div style="height:8px"/>', unsafe_allow_html=True)
        st.info('Gunakan filter di sisi kiri untuk melihat hasil segmentasi berdasarkan periode, divisi, dan jenis ATK tertentu.')
