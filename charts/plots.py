import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import PALETTE, MONTH_NAMES
from ui import label_color
from data.processor import best_k_index


# ── Internal helpers ──────────────────────────────────────────────────────────

def _base_layout(title, **kwargs):
    layout = dict(
        title=dict(text=title, font=dict(size=13, color=PALETTE['bg_dark'])),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=54, b=48, l=64, r=24),
        font=dict(family='Segoe UI, Inter, Arial, sans-serif', size=11, color=PALETTE['text_dark']),
        hoverlabel=dict(bgcolor='white', font_size=11, font_family='Segoe UI, Inter, Arial, sans-serif'),
    )
    layout.update(kwargs)
    return layout


def _rgba(hex_color, alpha=0.16):
    color = hex_color.lstrip('#')
    r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{alpha})'


def _convex_hull(points):
    pts = sorted(set(tuple(p) for p in points if np.isfinite(p[0]) and np.isfinite(p[1])))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _cluster_area(points):
    clean = np.array([p for p in points if np.isfinite(p[0]) and np.isfinite(p[1])], dtype=float)
    if len(clean) == 0:
        return []

    hull = _convex_hull(clean)
    if len(hull) >= 3:
        return hull

    center = clean.mean(axis=0)
    spread = clean.std(axis=0)
    x_span = max(clean[:, 0].max() - clean[:, 0].min(), spread[0], 1.0)
    y_span = max(clean[:, 1].max() - clean[:, 1].min(), spread[1], 1.0)
    rx = x_span * 0.65
    ry = y_span * 0.65
    angles = np.linspace(0, 2 * np.pi, 28, endpoint=False)
    return [(center[0] + rx * np.cos(a), center[1] + ry * np.sin(a)) for a in angles]


# ── Public chart functions ────────────────────────────────────────────────────

def chart_scatter(df, x, y, label, title):
    fig = go.Figure()
    labels = list(df[label].dropna().unique())
    symbols = ['circle', 'triangle-up', 'square', 'diamond', 'cross']

    for i, cluster_name in enumerate(labels):
        sub = df[df[label] == cluster_name].copy()
        color = label_color(cluster_name, i)
        hull = _cluster_area(sub[[x, y]].dropna().to_numpy())
        if len(hull) >= 3:
            hx, hy = zip(*(hull + [hull[0]]))
            fig.add_trace(go.Scatter(
                x=hx, y=hy, mode='lines',
                fill='toself',
                fillcolor=_rgba(color, 0.15),
                line=dict(color=color, width=1.2),
                hoverinfo='skip',
                showlegend=False,
            ))

        hover_cols = [c for c in df.columns if c not in [x, y]]
        customdata = sub[hover_cols].to_numpy() if hover_cols else None
        hover_lines = [f'<b>{cluster_name}</b>', f'{x}: %{{x:,.2f}}', f'{y}: %{{y:,.2f}}']
        hover_lines.extend([f'{col}: %{{customdata[{j}]}}' for j, col in enumerate(hover_cols[:6])])
        fig.add_trace(go.Scatter(
            x=sub[x],
            y=sub[y],
            mode='markers',
            name=str(cluster_name),
            customdata=customdata,
            hovertemplate='<br>'.join(hover_lines) + '<extra></extra>',
            marker=dict(
                color=color,
                symbol=symbols[i % len(symbols)],
                size=9,
                opacity=0.92,
                line=dict(width=1.1, color='white'),
            ),
        ))

        centroid = sub[[x, y]].mean()
        fig.add_trace(go.Scatter(
            x=[centroid[x]],
            y=[centroid[y]],
            mode='markers+text',
            name=f'Centroid {cluster_name}',
            text=['Centroid'],
            textposition='top center',
            hovertemplate=f'<b>Centroid {cluster_name}</b><br>{x}: %{{x:,.2f}}<br>{y}: %{{y:,.2f}}<extra></extra>',
            marker=dict(color='black', symbol='x', size=15, line=dict(width=3, color='black')),
            showlegend=False,
        ))

    fig.update_layout(
        **_base_layout(title, height=410),
        legend=dict(
            bgcolor='rgba(255,255,255,0.85)', bordercolor=PALETTE['border'], borderwidth=1,
            font=dict(size=10, color=PALETTE['text_dark']),
            title=dict(text=label, font=dict(size=10, color=PALETTE['text_dark'])),
            orientation='v', yanchor='top', y=0.98, xanchor='left', x=1.01,
        ),
    )
    fig.update_xaxes(
        title_text=x, showgrid=True, gridcolor='#E8EEF6', zeroline=False, automargin=True,
        tickfont=dict(color=PALETTE['text_dark']), title=dict(font=dict(color=PALETTE['text_dark'])),
    )
    fig.update_yaxes(
        title_text=y, showgrid=True, gridcolor='#E8EEF6', zeroline=False, automargin=True,
        tickfont=dict(color=PALETTE['text_dark']), title=dict(font=dict(color=PALETTE['text_dark'])),
    )
    return fig


def chart_donut(df, label_col, title):
    counts = df.groupby(label_col).size().reset_index(name='Jumlah')
    total  = len(df)
    fig = px.pie(
        counts, names=label_col, values='Jumlah',
        color=label_col,
        color_discrete_map={label: label_color(label, i) for i, label in enumerate(counts[label_col])},
        hole=0.55,
    )
    fig.update_layout(
        **_base_layout(title, margin=dict(t=54, b=36, l=20, r=20)),
        legend=dict(orientation='h', font=dict(size=10, color=PALETTE['text_dark']),
                    x=0.5, y=-0.08, xanchor='center'),
        annotations=[dict(
            text=f'Total<br><b>{total}</b><br>Divisi',
            x=0.5, y=0.5, font=dict(size=11, color=PALETTE['bg_dark']), showarrow=False,
        )],
    )
    fig.update_traces(
        textinfo='label+percent', textposition='outside',
        textfont=dict(size=11, color=PALETTE['text_dark']),
        marker=dict(line=dict(color='white', width=2)),
    )
    return fig


def chart_bar_top(df, value_col, cat_col, title, top_n=10, orientation='h'):
    top = df.nlargest(top_n, value_col).sort_values(value_col, ascending=True)
    if orientation == 'h':
        fig = px.bar(top, x=value_col, y=cat_col, orientation='h',
                     color_discrete_sequence=[PALETTE['secondary']])
        fig.update_layout(
            **_base_layout(title, margin=dict(t=54, b=42, l=150, r=24), height=390),
            xaxis=dict(showgrid=True, gridcolor='#E8EEF6', zeroline=False,
                       tickfont=dict(color=PALETTE['text_dark']),
                       title=dict(font=dict(color=PALETTE['text_dark']))),
            yaxis=dict(showgrid=False, zeroline=False, automargin=True,
                       tickfont=dict(color=PALETTE['text_dark']),
                       title=dict(font=dict(color=PALETTE['text_dark']))),
            showlegend=False,
        )
    else:
        top = top.sort_values(value_col, ascending=False)
        fig = px.bar(top, x=cat_col, y=value_col, orientation='v',
                     color_discrete_sequence=[PALETTE['bg']])
        fig.update_layout(
            **_base_layout(title, height=390),
            xaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(color=PALETTE['text_dark']),
                       title=dict(font=dict(color=PALETTE['text_dark']))),
            yaxis=dict(showgrid=True, gridcolor='#E8EEF6', zeroline=False,
                       tickfont=dict(color=PALETTE['text_dark']),
                       title=dict(font=dict(color=PALETTE['text_dark']))),
            showlegend=False,
        )
    fig.update_traces(
        texttemplate='%{x:,.0f}' if orientation == 'h' else '%{y:,.0f}',
        textposition='outside', cliponaxis=False,
        textfont=dict(color=PALETTE['text_dark'], size=10),
    )
    return fig


def chart_trend(df, title):
    trend = df.dropna(subset=['Tahun']).groupby('Tahun')['Jumlah'].sum().reset_index()
    trend['Tahun'] = trend['Tahun'].astype(int).astype(str)
    fig = px.line(trend, x='Tahun', y='Jumlah', markers=True,
                  color_discrete_sequence=[PALETTE['bg']])
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=9, color=PALETTE['accent'], line=dict(width=2, color=PALETTE['bg'])),
    )
    fig.update_layout(
        **_base_layout(title, height=360),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color=PALETTE['text_dark']),
                   title=dict(font=dict(color=PALETTE['text_dark']))),
        yaxis=dict(showgrid=True, gridcolor='#E8EEF6', zeroline=False,
                   tickfont=dict(color=PALETTE['text_dark']),
                   title=dict(font=dict(color=PALETTE['text_dark']))),
        showlegend=False,
    )
    return fig


def chart_time_monthly(monthly, title):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly['Bulan_Nama'], y=monthly['Frekuensi'],
        name='Frekuensi', marker_color=PALETTE['bg'], yaxis='y',
    ))
    fig.add_trace(go.Scatter(
        x=monthly['Bulan_Nama'], y=monthly['Total_Unit'],
        name='Total Unit', mode='lines+markers',
        marker=dict(size=8, color=PALETTE['accent']),
        line=dict(width=2.5, color=PALETTE['accent']),
        yaxis='y2',
    ))
    fig.update_layout(**_base_layout(
        title, height=420,
        yaxis=dict(title='Frekuensi', showgrid=True, gridcolor='#E8EEF6', zeroline=False),
        yaxis2=dict(title='Total Unit', overlaying='y', side='right', showgrid=False, zeroline=False),
        legend=dict(orientation='h', y=1.08, x=1, xanchor='right', font=dict(color=PALETTE['text_dark'])),
    ))
    return fig


def chart_time_period(period_summary, title):
    fig = px.bar(
        period_summary, x='Periode_Tahun', y='Frekuensi', text='Frekuensi',
        color='Periode_Tahun',
        color_discrete_sequence=[PALETTE['bg'], PALETTE['accent_light'], PALETTE['accent']],
    )
    fig.update_layout(**_base_layout(title, height=360, showlegend=False))
    fig.update_traces(textposition='outside', textfont=dict(color=PALETTE['text_dark'], size=11))
    fig.update_xaxes(tickfont=dict(color=PALETTE['text_dark']), title=None)
    fig.update_yaxes(tickfont=dict(color=PALETTE['text_dark']), title='Frekuensi', gridcolor='#E8EEF6')
    return fig


def chart_division_month_heatmap(df, title):
    data = df.dropna(subset=['Tanggal_Permintaan']).copy()
    data['Bulan'] = data['Tanggal_Permintaan'].dt.month
    data['Bulan_Nama'] = data['Bulan'].map(MONTH_NAMES)
    top_div = data.groupby('Divisi').size().nlargest(15).index
    data = data[data['Divisi'].isin(top_div)]
    pivot = data.pivot_table(
        index='Divisi', columns='Bulan_Nama', values='Jumlah', aggfunc='count', fill_value=0
    )
    month_order = [MONTH_NAMES[i] for i in range(1, 13)]
    pivot = pivot.reindex(columns=[m for m in month_order if m in pivot.columns], fill_value=0)
    fig = px.imshow(pivot, color_continuous_scale='Blues', aspect='auto', text_auto=True)
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=PALETTE['bg_dark'])),
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Segoe UI, Inter, Arial, sans-serif', size=10, color=PALETTE['text_dark']),
        margin=dict(t=54, b=60, l=150, r=24),
        height=450,
        coloraxis_colorbar=dict(title='Frekuensi'),
    )
    fig.update_xaxes(tickfont=dict(size=9, color=PALETTE['text_dark']))
    fig.update_yaxes(tickfont=dict(size=9, color=PALETTE['text_dark']), automargin=True)
    fig.update_traces(textfont=dict(color=PALETTE['text_dark'], size=9))
    return fig


def chart_heatmap(m3, title, top_div=10, top_item=7):
    top_d = m3.groupby('Divisi')['Skor_Ketergantungan'].max().nlargest(top_div).index
    top_i = m3.groupby('Jenis_ATK')['Skor_Ketergantungan'].max().nlargest(top_item).index
    sub   = m3[m3['Divisi'].isin(top_d) & m3['Jenis_ATK'].isin(top_i)]
    pivot = sub.pivot_table(
        index='Divisi', columns='Jenis_ATK', values='Skor_Ketergantungan', fill_value=0
    )
    fig = px.imshow(pivot, color_continuous_scale='RdYlBu_r', aspect='auto', text_auto='.2f')
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=PALETTE['bg_dark'])),
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Segoe UI, Inter, Arial, sans-serif', size=10, color=PALETTE['text_dark']),
        margin=dict(t=54, b=96, l=150, r=24),
        height=430,
        coloraxis_colorbar=dict(title='Skor', len=0.8, tickfont=dict(size=9)),
    )
    fig.update_xaxes(tickangle=-35, tickfont=dict(size=9), automargin=True)
    fig.update_yaxes(tickfont=dict(size=9), automargin=True)
    fig.update_traces(textfont=dict(color=PALETTE['text_dark'], size=10))
    return fig


def chart_sankey(m3, title, label_filter='Prioritas Tinggi'):
    data = m3[m3['Label'] == label_filter].copy()
    if data.empty:
        data = m3.copy()
    data = data.sort_values('Skor_Ketergantungan', ascending=False)

    divisi_nodes = data['Divisi'].dropna().unique().tolist()
    item_nodes   = data['Jenis_ATK'].dropna().unique().tolist()
    label_nodes  = data['Label'].dropna().unique().tolist()

    node_keys = (
        [('Divisi', name) for name in divisi_nodes] +
        [('Item',   name) for name in item_nodes]   +
        [('Label',  name) for name in label_nodes]
    )
    labels = [name for _, name in node_keys]
    index  = {key: i for i, key in enumerate(node_keys)}
    node_colors = (
        [_rgba(PALETTE['bg'], 0.85)]            * len(divisi_nodes) +
        [_rgba(PALETTE['accent'], 0.82)]         * len(item_nodes)  +
        [_rgba(PALETTE['cluster_colors'][2], 0.82)] * len(label_nodes)
    )

    left  = data.groupby(['Divisi', 'Jenis_ATK'], as_index=False)['Total_Jumlah'].sum()
    right = data.groupby(['Jenis_ATK', 'Label'],  as_index=False)['Total_Jumlah'].sum()
    sources = [index[('Divisi', row['Divisi'])]   for _, row in left.iterrows()]
    targets = [index[('Item',   row['Jenis_ATK'])] for _, row in left.iterrows()]
    values  = left['Total_Jumlah'].tolist()
    sources += [index[('Item',  row['Jenis_ATK'])] for _, row in right.iterrows()]
    targets += [index[('Label', row['Label'])]     for _, row in right.iterrows()]
    values  += right['Total_Jumlah'].tolist()

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=22, thickness=18,
            line=dict(color=PALETTE['border'], width=0.7),
            label=labels, color=node_colors,
        ),
        link=dict(source=sources, target=targets, value=values, color='rgba(21,101,192,0.18)'),
    )])
    chart_height = max(520, min(980, 28 * len(labels)))
    fig.update_layout(**_base_layout(
        title, height=chart_height,
        margin=dict(t=58, b=34, l=28, r=28),
        font=dict(family='Arial, sans-serif', size=13, color=PALETTE['text_dark']),
    ))
    return fig


def show_eval_table(results):
    idx     = best_k_index(results)
    best    = results[idx]
    sil_k   = max(results, key=lambda r: r['Silhouette'])['K']
    dbi_k   = min(results, key=lambda r: r['DBI'])['K']
    summary = pd.DataFrame([{
        'K': r['K'],
        'WCSS': round(r['WCSS'], 4),
        'Silhouette': round(r['Silhouette'], 4),
        'DBI': round(r['DBI'], 4),
    } for r in results]).set_index('K')
    st.table(summary)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric('Silhouette Tertinggi', f'K = {sil_k}', f'{best["Silhouette"]:.4f}')
    with c2: st.metric('DBI Terendah', f'K = {dbi_k}', f'{min(r["DBI"] for r in results):.4f}')
    with c3: st.success(f'**K Terpilih = {best["K"]}**')
    return idx, best['K']
