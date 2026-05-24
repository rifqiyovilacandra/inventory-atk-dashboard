import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import RobustScaler


@st.cache_data
def prepare_data(df):
    df = df.drop_duplicates().copy()
    df['Tanggal_Permintaan'] = pd.to_datetime(df['Tanggal_Permintaan'], errors='coerce')
    df['Tahun'] = df['Tanggal_Permintaan'].dt.year
    df = df.drop(columns=['Tanggal_Persetujuan', 'Unit'])
    df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
    df = df.dropna(subset=['Jenis_ATK', 'Divisi', 'Jumlah']).reset_index(drop=True)
    df = df[df['Jumlah'] > 0].reset_index(drop=True)
    return df


@st.cache_data
def normalize_dataframe(df, columns):
    scaler = RobustScaler()
    values = scaler.fit_transform(df[columns].values)
    out = df.copy()
    for i, col in enumerate(columns):
        out[f'{col}_norm'] = values[:, i]
    return out, scaler


@st.cache_data
def evaluate_kmeans(X, k_values=(2, 3)):
    results = []
    for k in k_values:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        sil = silhouette_score(X, labels) if len(np.unique(labels)) > 1 else np.nan
        dbi = davies_bouldin_score(X, labels) if len(np.unique(labels)) > 1 else np.nan
        results.append({
            'K': k,
            'WCSS': float(model.inertia_),
            'Silhouette': float(sil),
            'DBI': float(dbi),
            'labels': labels,
            'centroids': model.cluster_centers_,
        })
    return results


def best_k_index(results):
    return int(np.argmax([r['Silhouette'] for r in results]))


def cluster_label_map(df, sort_col, prefix):
    order = df.groupby('Cluster_ID')[sort_col].mean().sort_values(ascending=False).index.tolist()
    n = len(order)
    if prefix == 'Konsumsi':
        labels = ['Tinggi', 'Rendah'] if n == 2 else ['Tinggi', 'Sedang', 'Rendah'][:n]
    elif prefix == 'Moving':
        labels = ['Fast Moving', 'Slow Moving'] if n == 2 else ['Fast Moving', 'Medium Moving', 'Slow Moving'][:n]
    else:
        labels = ['Prioritas Tinggi', 'Prioritas Rendah'] if n == 2 else ['Prioritas Tinggi', 'Prioritas Sedang', 'Prioritas Rendah'][:n]
    return {cid: labels[i] for i, cid in enumerate(order)}


def compute_model1(df):
    agg = df.groupby('Divisi').agg(
        Volume=('Jumlah', 'sum'),
        Frekuensi=('Jumlah', 'count'),
    ).reset_index()
    m = agg[agg['Frekuensi'] >= 5].reset_index(drop=True)
    if len(m) < 6:
        return None, None
    norm, _ = normalize_dataframe(m, ['Volume', 'Frekuensi'])
    results = evaluate_kmeans(norm[['Volume_norm', 'Frekuensi_norm']].values)
    idx = best_k_index(results)
    norm = norm.copy()
    norm['Cluster_ID'] = results[idx]['labels']
    norm['Cluster'] = norm['Cluster_ID'].apply(lambda x: f'C{x+1}')
    norm['Label'] = norm['Cluster_ID'].map(cluster_label_map(norm, 'Volume', 'Konsumsi'))
    return norm, results


def compute_model2(df):
    agg = df.groupby('Jenis_ATK').agg(
        Total_Jumlah=('Jumlah', 'sum'),
        Frekuensi=('Jumlah', 'count'),
        Rata_per_Req=('Jumlah', 'mean'),
        Jumlah_Divisi=('Divisi', 'nunique'),
    ).reset_index()
    m = agg[agg['Frekuensi'] >= 3].reset_index(drop=True)
    if len(m) < 6:
        return None, None
    feat_cols = ['Total_Jumlah', 'Frekuensi', 'Rata_per_Req', 'Jumlah_Divisi']
    norm, _ = normalize_dataframe(m, feat_cols)
    results = evaluate_kmeans(norm[[c + '_norm' for c in feat_cols]].values)
    idx = best_k_index(results)
    norm = norm.copy()
    norm['Cluster_ID'] = results[idx]['labels']
    norm['Cluster'] = norm['Cluster_ID'].apply(lambda x: f'C{x+1}')
    norm['Label'] = norm['Cluster_ID'].map(cluster_label_map(norm, 'Frekuensi', 'Moving'))
    return norm, results


def compute_model3(df):
    base = df.groupby(['Divisi', 'Jenis_ATK']).agg(
        Total_Jumlah=('Jumlah', 'sum'),
        Frekuensi=('Jumlah', 'count'),
    ).reset_index()
    m = base[base['Frekuensi'] >= 2].reset_index(drop=True)
    if len(m) < 6:
        return None, None
    tot_item = df.groupby('Jenis_ATK')['Jumlah'].sum().rename('Total_Item_Semua').reset_index()
    tot_div  = df.groupby('Divisi')['Jumlah'].sum().rename('Total_Divisi_Semua').reset_index()
    m = m.merge(tot_item, on='Jenis_ATK').merge(tot_div, on='Divisi')
    m['Share_Divisi_Terhadap_Item'] = m['Total_Jumlah'] / m['Total_Item_Semua']
    m['Share_Item_Dalam_Divisi']    = m['Total_Jumlah'] / m['Total_Divisi_Semua']
    m['Frek_Rank']  = m['Frekuensi'].rank(pct=True)
    m['Total_Rank'] = m['Total_Jumlah'].rank(pct=True)
    m['Skor_Ketergantungan'] = (
        0.35 * m['Share_Divisi_Terhadap_Item'] + 0.35 * m['Share_Item_Dalam_Divisi'] +
        0.10 * m['Frek_Rank'] + 0.20 * m['Total_Rank']
    )
    feat_cols = [
        'Total_Jumlah', 'Frekuensi', 'Share_Divisi_Terhadap_Item',
        'Share_Item_Dalam_Divisi', 'Skor_Ketergantungan',
    ]
    norm, _ = normalize_dataframe(m, feat_cols)
    results = evaluate_kmeans(norm[[c + '_norm' for c in feat_cols]].values)
    idx = best_k_index(results)
    norm = norm.copy()
    norm['Cluster_ID'] = results[idx]['labels']
    norm['Cluster'] = norm['Cluster_ID'].apply(lambda x: f'C{x+1}')
    norm['Label'] = norm['Cluster_ID'].map(cluster_label_map(norm, 'Skor_Ketergantungan', 'Prioritas'))
    return norm, results
