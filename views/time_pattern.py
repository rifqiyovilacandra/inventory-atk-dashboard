import streamlit as st

from data.time_pattern import compute_time_pattern
from charts.plots import (
    chart_time_monthly, chart_time_period, chart_division_month_heatmap,
)
from ui import section_header


def page_time_pattern(df):
    section_header(
        'Analisis Pola Waktu Permintaan ATK',
        'Analisis deskriptif untuk mengetahui kapan divisi cenderung melakukan permintaan ATK',
    )

    divisi_options = sorted(df['Divisi'].dropna().unique().tolist())
    selected_divisi = st.selectbox('Pilih Divisi', divisi_options, key='time_pattern_divisi')
    data, monthly, period_summary, item_month, insight = compute_time_pattern(df, selected_divisi)
    if data.empty:
        st.warning('Data tanggal permintaan untuk divisi ini tidak tersedia atau tidak dapat dibaca.')
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric('Total Transaksi', f'{len(data):,}')
    with c2: st.metric('Total Unit',      f'{data["Jumlah"].sum():,.0f}')
    with c3: st.metric('Bulan Aktif',     f'{monthly["Bulan"].nunique():,}')
    with c4:
        top_period = period_summary.sort_values('Frekuensi', ascending=False).iloc[0]['Periode_Tahun']
        st.metric('Periode Dominan', str(top_period))

    st.info(insight)

    p1, p2 = st.columns([3, 2])
    with p1:
        st.plotly_chart(
            chart_time_monthly(monthly, f'Pola Bulanan Permintaan - {selected_divisi}'),
            use_container_width=True,
        )
    with p2:
        st.plotly_chart(
            chart_time_period(period_summary, f'Distribusi Periode Tahun - {selected_divisi}'),
            use_container_width=True,
        )

    st.plotly_chart(
        chart_division_month_heatmap(df, 'Heatmap Frekuensi Permintaan Divisi per Bulan'),
        use_container_width=True,
    )

    st.write('#### Detail Pola Bulanan')
    monthly_detail = monthly[['Bulan_Nama', 'Frekuensi', 'Total_Unit']].rename(columns={'Bulan_Nama': 'Bulan'})
    st.dataframe(monthly_detail, use_container_width=True)

    st.write('#### Item ATK Dominan per Bulan')
    top_item_month = item_month.groupby('Bulan_Nama').head(3).reset_index(drop=True)
    st.dataframe(
        top_item_month[['Bulan_Nama', 'Jenis_ATK', 'Frekuensi', 'Total_Unit']].rename(
            columns={'Bulan_Nama': 'Bulan'}
        ),
        use_container_width=True,
    )

    st.write('#### Kenapa Fitur Ini Tidak Menggunakan Clustering?')
    st.markdown("""
    Analisis pola waktu ini tidak menggunakan K-Means karena tujuan analisisnya berbeda. K-Means digunakan untuk
    mengelompokkan objek berdasarkan kemiripan karakteristik, sedangkan fitur ini bertujuan membaca pola historis
    permintaan berdasarkan kalender: bulan, periode awal/tengah/akhir tahun, dan frekuensi permintaan.

    Dengan pendekatan deskriptif berbasis aturan, hasilnya lebih mudah dijelaskan: sistem menghitung frekuensi dan
    volume permintaan per periode, lalu menyimpulkan apakah sebuah divisi dominan pada awal tahun, tengah tahun,
    akhir tahun, atau relatif merata. Karena tidak ada kebutuhan membentuk kelompok baru, clustering tidak diperlukan.
    """)
