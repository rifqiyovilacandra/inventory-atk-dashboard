import pandas as pd

from config import MONTH_NAMES


def year_period(month):
    if month <= 4:
        return 'Awal Tahun'
    if month <= 8:
        return 'Tengah Tahun'
    return 'Akhir Tahun'


def time_pattern_insight(monthly, period_summary, divisi):
    if monthly.empty:
        return f'Divisi {divisi} belum memiliki data permintaan yang dapat dianalisis.'

    total = period_summary['Frekuensi'].sum()
    top_period = period_summary.sort_values('Frekuensi', ascending=False).iloc[0]
    top_months = monthly.sort_values(['Frekuensi', 'Total_Unit'], ascending=False).head(2)
    month_text = ', '.join(top_months['Bulan_Nama'].tolist())
    period_share = (top_period['Frekuensi'] / total * 100) if total else 0
    month_counts = monthly['Frekuensi'].to_numpy()
    is_even = len(month_counts) >= 6 and month_counts.std() <= max(1, month_counts.mean() * 0.35)

    if period_share >= 45:
        return (
            f'Divisi {divisi} cenderung melakukan permintaan pada {top_period["Periode_Tahun"]} '
            f'({period_share:.0f}% dari frekuensi permintaan), terutama pada bulan {month_text}.'
        )
    if is_even:
        return f'Divisi {divisi} memiliki pola permintaan yang relatif merata sepanjang tahun.'
    return (
        f'Divisi {divisi} paling sering melakukan permintaan pada bulan {month_text}, '
        f'namun tidak dominan pada satu periode tahun.'
    )


def compute_time_pattern(df, divisi):
    data = df[df['Divisi'] == divisi].copy()
    data = data.dropna(subset=['Tanggal_Permintaan'])
    data['Bulan'] = data['Tanggal_Permintaan'].dt.month
    data['Bulan_Nama'] = data['Bulan'].map(MONTH_NAMES)
    data['Periode_Tahun'] = data['Bulan'].apply(year_period)
    data['Tanggal_Bulan'] = data['Tanggal_Permintaan'].dt.day

    monthly = data.groupby(['Bulan', 'Bulan_Nama'], as_index=False).agg(
        Frekuensi=('Jumlah', 'count'),
        Total_Unit=('Jumlah', 'sum'),
    ).sort_values('Bulan')

    period_order = ['Awal Tahun', 'Tengah Tahun', 'Akhir Tahun']
    period_summary = data.groupby('Periode_Tahun', as_index=False).agg(
        Frekuensi=('Jumlah', 'count'),
        Total_Unit=('Jumlah', 'sum'),
    )
    period_summary['Periode_Tahun'] = pd.Categorical(
        period_summary['Periode_Tahun'], period_order, ordered=True
    )
    period_summary = period_summary.sort_values('Periode_Tahun')

    item_month = data.groupby(['Bulan', 'Bulan_Nama', 'Jenis_ATK'], as_index=False).agg(
        Frekuensi=('Jumlah', 'count'),
        Total_Unit=('Jumlah', 'sum'),
    ).sort_values(['Bulan', 'Frekuensi'], ascending=[True, False])

    insight = time_pattern_insight(monthly, period_summary, divisi)
    return data, monthly, period_summary, item_month, insight
