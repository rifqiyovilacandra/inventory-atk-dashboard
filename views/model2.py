import streamlit as st

from data.processor import best_k_index
from charts.plots import chart_scatter, chart_donut, show_eval_table
from ui import section_header, filter_dataframe


def page_model2(df, m2, results):
    section_header(
        'Model 2 - Segmentasi Pergerakan Produk ATK',
        'Klasifikasi produk ATK berdasarkan frekuensi dan volume permintaan',
    )
    if m2 is None:
        st.warning('Data tidak cukup untuk Model 2 dengan filter saat ini.')
        return

    best_k = results[best_k_index(results)]['K']

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric('Produk Dianalisis',   f'{len(m2):,}')
    with c2: st.metric('Total Permintaan',    f'{m2["Total_Jumlah"].sum():,.0f}', 'Unit')
    with c3: st.metric('Rata-rata Frekuensi', f'{m2["Frekuensi"].mean():.1f}', 'Transaksi')
    with c4: st.metric('Rata-rata Divisi',    f'{m2["Jumlah_Divisi"].mean():.1f}', 'Divisi')

    st.info('Hanya produk dengan frekuensi transaksi minimal 3 yang dianalisis.')

    cc1, cc2 = st.columns([3, 2])
    with cc1:
        st.plotly_chart(
            chart_scatter(m2, 'Total_Jumlah', 'Frekuensi', 'Label',
                          f'Model 2 - Scatter Pergerakan Produk (K={best_k})'),
            use_container_width=True,
        )
    with cc2:
        st.plotly_chart(chart_donut(m2, 'Label', 'Proporsi Cluster Produk'), use_container_width=True)

    st.write('#### Data Segmentasi Produk')
    data_m2 = m2[['Jenis_ATK', 'Total_Jumlah', 'Frekuensi', 'Rata_per_Req', 'Jumlah_Divisi', 'Cluster', 'Label']]
    data_m2 = data_m2.sort_values('Frekuensi', ascending=False).reset_index(drop=True)
    st.dataframe(filter_dataframe(data_m2, 'search_model2'), use_container_width=True)

    st.write('#### Ringkasan Cluster Produk')
    st.dataframe(
        m2.groupby(['Cluster', 'Label']).agg(
            Jumlah_Produk=('Jenis_ATK', 'count'),
            Rata_Frekuensi=('Frekuensi', 'mean'),
            Rata_Total_Jumlah=('Total_Jumlah', 'mean'),
        ).reset_index().round(2), use_container_width=True,
    )

    st.write('#### Evaluasi K-Means')
    show_eval_table(results)
