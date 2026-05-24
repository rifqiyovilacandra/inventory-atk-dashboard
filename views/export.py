import streamlit as st

from config import PALETTE
from exports.excel import to_excel
from exports.pdf import to_pdf_report
from ui import section_header


def page_export(df, m1, m2, m3, m1_res, m2_res, m3_res):
    section_header('Export & Laporan', 'Unduh hasil segmentasi dalam format Excel dan PDF')

    sheets = {}
    if m1 is not None:
        sheets['1-Segmentasi Konsumsi Divisi'] = m1[['Divisi', 'Volume', 'Frekuensi', 'Cluster', 'Label']]
    if m2 is not None:
        sheets['2-Segmentasi Pergerakan ATK'] = m2[[
            'Jenis_ATK', 'Total_Jumlah', 'Frekuensi', 'Rata_per_Req', 'Jumlah_Divisi', 'Cluster', 'Label'
        ]]
    if m3 is not None:
        sheets['3-Prioritas Divisi-Item'] = m3[[
            'Divisi', 'Jenis_ATK', 'Total_Jumlah', 'Frekuensi', 'Skor_Ketergantungan', 'Cluster', 'Label'
        ]]

    if not sheets:
        st.warning('Tidak ada data yang dapat diekspor. Pastikan dataset sudah diunggah dan filter sesuai.')
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style='background:white;border:1px solid {PALETTE["border"]};border-radius:12px;
                    padding:28px 24px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    margin-bottom:12px;'>
            <div style='font-size:2.8rem;color:{PALETTE["bg_dark"]};font-weight:800;'>XLSX</div>
            <h4 style='color:{PALETTE["bg_dark"]};margin:10px 0 4px;'>Export ke Excel</h4>
            <p style='color:#888;font-size:0.83rem;margin-bottom:0;'>Format .xlsx — semua model dalam satu file</p>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label='📥  Unduh Excel (.xlsx)',
            data=to_excel(sheets),
            file_name='segmentasi_atk.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True,
        )
    with c2:
        st.markdown(f"""
        <div style='background:white;border:1px solid {PALETTE["border"]};border-radius:12px;
                    padding:28px 24px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    margin-bottom:12px;'>
            <div style='font-size:2.8rem;color:{PALETTE["accent"]};font-weight:800;'>PDF</div>
            <h4 style='color:{PALETTE["bg_dark"]};margin:10px 0 4px;'>Export ke PDF</h4>
            <p style='color:#888;font-size:0.83rem;margin-bottom:0;'>Laporan ringkas Overview, Model 1, Model 2, dan Model 3</p>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label='Unduh Laporan PDF',
            data=to_pdf_report(df, m1, m2, m3, m1_res, m2_res, m3_res),
            file_name='laporan_segmentasi_atk.pdf',
            mime='application/pdf',
            use_container_width=True,
        )

    st.markdown('---')
    st.info('Informasi: Gunakan filter di sisi kiri untuk melihat hasil segmentasi berdasarkan periode, divisi, dan jenis ATK tertentu.')
