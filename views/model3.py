import streamlit as st

from data.processor import best_k_index
from charts.plots import chart_scatter, chart_heatmap, chart_sankey, show_eval_table
from ui import section_header, filter_dataframe


def page_model3(df, m3, results):
    section_header(
        'Model 3 - Segmentasi Prioritas Divisi-Item ATK',
        'Pasangan divisi-item diurutkan berdasarkan skor ketergantungan',
    )
    if m3 is None:
        st.warning('Data tidak cukup untuk Model 3 dengan filter saat ini.')
        return

    best_k     = results[best_k_index(results)]['K']
    high_label = 'Prioritas Tinggi'

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric('Pasangan Divisi-Item', f'{len(m3):,}')
    with c2: st.metric('Total Volume',         f'{m3["Total_Jumlah"].sum():,.0f}', 'Unit')
    with c3: st.metric('Rata-rata Skor',       f'{m3["Skor_Ketergantungan"].mean():.3f}')
    with c4: st.metric('Prioritas Tinggi',     f'{(m3["Label"] == high_label).sum():,}')

    st.info('Hanya pasangan Divisi-Item dengan frekuensi transaksi minimal 2 yang dianalisis.')

    cs, ch = st.columns(2)
    with cs:
        st.plotly_chart(
            chart_scatter(m3, 'Total_Jumlah', 'Skor_Ketergantungan', 'Label',
                          f'Scatter Prioritas Divisi-Item (K={best_k})'),
            use_container_width=True,
        )
    with ch:
        st.plotly_chart(
            chart_heatmap(m3, 'Heatmap Prioritas Divisi-Item (Skor Ketergantungan)'),
            use_container_width=True,
        )

    st.plotly_chart(
        chart_sankey(m3, 'Sankey Divisi - Item ATK - Prioritas Cluster'),
        use_container_width=True,
    )

    st.write('#### Prioritas Divisi-Item')
    data_m3 = m3[['Divisi', 'Jenis_ATK', 'Total_Jumlah', 'Frekuensi', 'Skor_Ketergantungan', 'Cluster', 'Label']]
    data_m3 = data_m3.sort_values(['Label', 'Skor_Ketergantungan'], ascending=[True, False]).reset_index(drop=True)
    st.dataframe(filter_dataframe(data_m3, 'search_model3'), use_container_width=True)

    st.write('#### Ringkasan Cluster')
    st.dataframe(
        m3.groupby(['Cluster', 'Label']).agg(
            Jumlah_Pasangan=('Divisi', 'count'),
            Rata_Skor=('Skor_Ketergantungan', 'mean'),
            Rata_Frekuensi=('Frekuensi', 'mean'),
        ).reset_index().round(4), use_container_width=True,
    )

    st.write('#### Evaluasi K-Means')
    show_eval_table(results)
