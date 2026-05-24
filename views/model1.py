import streamlit as st

from data.processor import best_k_index
from data.time_pattern import compute_time_pattern
from charts.plots import chart_scatter, chart_donut, chart_time_monthly, chart_time_period, show_eval_table
from ui import section_header, filter_dataframe


def page_model1(df, m1, results):
    section_header(
        'Model 1 - Segmentasi Konsumsi Divisi',
        'Pengelompokan divisi berdasarkan volume dan frekuensi permintaan ATK',
    )
    if m1 is None:
        st.warning('Data tidak cukup untuk Model 1 dengan filter saat ini '
                   '(butuh minimal 6 divisi dengan frekuensi transaksi minimal 5).')
        return

    best_k = results[best_k_index(results)]['K']

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric('Divisi Dianalisis',   f'{len(m1):,}')
    with c2: st.metric('Total Volume',        f'{m1["Volume"].sum():,.0f}', 'Unit')
    with c3: st.metric('Rata-rata Frekuensi', f'{m1["Frekuensi"].mean():.1f}', 'Transaksi')
    with c4: st.metric('Cluster Aktif',       f'{m1["Label"].nunique():,}')

    st.info('Hanya divisi dengan frekuensi transaksi minimal 5 yang dianalisis.')

    cc1, cc2 = st.columns([3, 2])
    with cc1:
        st.plotly_chart(
            chart_scatter(m1, 'Volume', 'Frekuensi', 'Label',
                          f'Model 1 - Scatter Konsumsi Divisi (K={best_k})'),
            use_container_width=True,
        )
    with cc2:
        st.plotly_chart(chart_donut(m1, 'Label', 'Proporsi Cluster Divisi'), use_container_width=True)

    st.write('#### Data Permintaan Divisi')
    divisi_options = m1.sort_values('Volume', ascending=False)['Divisi'].tolist()
    selected_divisi = st.selectbox('Pilih divisi untuk melihat pola waktu', divisi_options, key='model1_time_divisi')
    time_data, monthly, period_summary, item_month, insight = compute_time_pattern(df, selected_divisi)
    if time_data.empty:
        st.warning('Data tanggal permintaan untuk divisi ini tidak tersedia atau tidak dapat dibaca.')
    else:
        st.info(insight)
        t1, t2, t3 = st.columns(3)
        with t1: st.metric('Transaksi Divisi', f'{len(time_data):,}')
        with t2: st.metric('Total Unit Divisi', f'{time_data["Jumlah"].sum():,.0f}')
        with t3:
            dominant_period = period_summary.sort_values('Frekuensi', ascending=False).iloc[0]['Periode_Tahun']
            st.metric('Periode Dominan', str(dominant_period))

        p1, p2 = st.columns([3, 2])
        with p1:
            st.plotly_chart(
                chart_time_monthly(monthly, f'Pola Bulanan - {selected_divisi}'),
                use_container_width=True,
            )
        with p2:
            st.plotly_chart(
                chart_time_period(period_summary, f'Periode Tahun - {selected_divisi}'),
                use_container_width=True,
            )

    st.write('#### Data Segmentasi Divisi')
    data_m1 = m1[['Divisi', 'Volume', 'Frekuensi', 'Cluster', 'Label']].sort_values(
        'Volume', ascending=False
    ).reset_index(drop=True)
    st.dataframe(filter_dataframe(data_m1, 'search_model1'), use_container_width=True)

    st.write('#### Ringkasan Cluster')
    st.dataframe(
        m1.groupby(['Cluster', 'Label']).agg(
            Jumlah_Divisi=('Divisi', 'count'),
            Rata_Volume=('Volume', 'mean'),
            Rata_Frekuensi=('Frekuensi', 'mean'),
        ).reset_index().round(2), use_container_width=True,
    )

    st.write('#### Evaluasi K-Means')
    show_eval_table(results)
