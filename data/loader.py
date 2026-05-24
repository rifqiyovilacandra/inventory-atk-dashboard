import pandas as pd
import streamlit as st

from config import REQUIRED_COLS


@st.cache_data
def load_and_validate(uploaded_file):
    try:
        df_raw = pd.read_excel(uploaded_file, skiprows=1)
    except Exception:
        return None, (
            "File tidak dapat dibaca sebagai Excel. "
            "Pastikan file berformat **.xlsx** atau **.xls** dan tidak rusak."
        )

    if df_raw.empty or len(df_raw) < 2:
        return None, (
            "File Excel tidak mengandung data yang cukup. "
            "Pastikan terdapat minimal **2 baris data** di bawah header."
        )

    if len(df_raw.columns) < 6:
        return None, (
            f"Jumlah kolom tidak sesuai: file memiliki **{len(df_raw.columns)} kolom**, "
            f"sedangkan dibutuhkan **6 kolom** dengan urutan:\n\n"
            f"| # | Kolom |\n|---|-------|\n"
            f"| 1 | Tanggal Persetujuan |\n"
            f"| 2 | Tanggal Permintaan |\n"
            f"| 3 | Jenis ATK |\n"
            f"| 4 | Divisi |\n"
            f"| 5 | Jumlah |\n"
            f"| 6 | Unit |"
        )

    df = df_raw.iloc[:, :6].copy()
    df.columns = REQUIRED_COLS

    for col, label in [('Jenis_ATK', 'Jenis ATK (kolom 3)'), ('Divisi', 'Divisi (kolom 4)')]:
        pct_null = df[col].isna().mean()
        if pct_null > 0.5:
            return None, (
                f"Kolom **{label}** terlalu banyak nilai kosong "
                f"({pct_null:.0%} dari {len(df):,} baris kosong). "
                f"Pastikan dataset ATK yang diunggah sesuai format."
            )

    jumlah_num = pd.to_numeric(df['Jumlah'], errors='coerce')
    valid_pct = jumlah_num.notna().mean()
    if valid_pct < 0.4:
        return None, (
            f"Kolom **Jumlah (kolom 5)** tidak mengandung cukup data numerik "
            f"(hanya {valid_pct:.0%} baris valid). "
            f"Pastikan kolom tersebut berisi angka jumlah permintaan ATK."
        )

    return df, None


def show_upload_error(message: str):
    st.markdown(f"""
    <div style='background:#FFF5F5;border:1.5px solid #FECACA;border-left:5px solid #DC2626;
                border-radius:10px;padding:20px 24px;margin:16px 0;'>
        <div style='display:flex;align-items:flex-start;gap:12px;'>
            <span style='font-size:1.6rem;line-height:1;'>⚠️</span>
            <div>
                <p style='color:#991B1B;font-weight:700;font-size:1rem;margin:0 0 6px;'>
                    Format Dataset Tidak Sesuai
                </p>
                <p style='color:#7F1D1D;font-size:0.88rem;margin:0;line-height:1.6;'>
                    {message}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander('📋  Lihat format dataset yang diharapkan', expanded=False):
        st.markdown("""
**Format file Excel ATK yang valid:**
- Ekstensi file: `.xlsx` atau `.xls`
- **Baris pertama** berisi informasi/judul (dilewati otomatis)
- **Baris kedua** adalah header kolom
- Minimal **6 kolom** dengan urutan yang tepat:

| No | Nama Kolom | Tipe Data |
|----|-----------|-----------|
| 1 | Tanggal Persetujuan | Tanggal |
| 2 | Tanggal Permintaan | Tanggal |
| 3 | Jenis ATK | Teks |
| 4 | Divisi | Teks |
| 5 | Jumlah | Angka |
| 6 | Unit | Teks |

> Gunakan file Excel yang sama seperti pada analisis awal di Google Colab.
        """)
