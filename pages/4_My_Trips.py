import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.mysql_connector import get_all_trips

# Compatibility for older Streamlit versions that may not have SecretsMissingError
try:
    from streamlit.errors import SecretsMissingError
except ImportError:
    class SecretsMissingError(Exception):
        pass

st.set_page_config(page_title="Trip Insights", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

.page-header { margin-bottom: 0.25rem; }
.hero-title { font-size: 2rem; font-weight: 800; color: #1a1a2e; margin: 0; }
.hero-title span { color: #0077B6; }
.hero-sub { font-size: 0.9rem; color: #94a3b8; margin: 0.25rem 0 0 0; }

.kpi-card {
    background: white; border-radius: 16px; padding: 1.1rem 1rem 1rem;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
    border-top: 3px solid #0077B6; text-align: center;
}
.kpi-card.orange { border-top-color: #FF6E40; }
.kpi-card.green  { border-top-color: #10b981; }
.kpi-card.purple { border-top-color: #8b5cf6; }
.kpi-card.teal   { border-top-color: #0ea5e9; }
.kpi-val   { font-size: 1.75rem; font-weight: 800; color: #1a1a2e; line-height: 1.1; }
.kpi-label { font-size: 0.75rem; color: #64748b; font-weight: 600; margin-top: 4px; letter-spacing: 0.03em; text-transform: uppercase; }
.kpi-sub   { font-size: 0.7rem; color: #94a3b8; margin-top: 2px; }

.section-label {
    font-size: 0.7rem; font-weight: 700; color: #0077B6;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;
}
.section-title { font-size: 1.05rem; font-weight: 700; color: #1a1a2e; margin: 0 0 0.75rem 0; }

.insight-box {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 1px solid #bae6fd; border-radius: 14px;
    padding: 1rem 1.2rem; margin: 0.5rem 0 1rem 0;
}
.insight-row { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.4rem; font-size: 0.88rem; color: #1e3a5f; }
.insight-row:last-child { margin-bottom: 0; }

.chart-card {
    background: white; border-radius: 16px; padding: 1.2rem 1.2rem 0.5rem;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06); height: 100%;
}
.badge-major { background:#dbeafe; color:#1d4ed8; border-radius:6px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.badge-secondary { background:#fff7ed; color:#c2410c; border-radius:6px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ── City type lookup จาก master CSV ──────────────────────────────────────────
def map_city_type_th(city_type_en):
    if city_type_en == 'Major City': return 'เมืองหลัก'
    if city_type_en == 'Secondary City': return 'เมืองรอง'
    return 'ไม่ทราบ'

@st.cache_data
def _load_province_city_type_map():
    """Build ProvinceThai → city_type_th lookup from master CSV."""
    try:
        _csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'master_tourism_analysis.csv')
        _df = pd.read_csv(_csv, usecols=['ProvinceThai', 'City_type_EN']).drop_duplicates(subset=['ProvinceThai'])
        return dict(zip(_df['ProvinceThai'], _df['City_type_EN'].map({'Major City': 'เมืองหลัก', 'Secondary City': 'เมืองรอง'}).fillna('ไม่ทราบ')))
    except Exception:
        return {}

_province_type_map = _load_province_city_type_map()

# ── Header ────────────────────────────────────────────────────────────────────
col_hd, col_refresh = st.columns([5, 1])
with col_hd:
    st.markdown('<div class="page-header">'
                '<h1 class="hero-title">📊 Trip <span>Insights</span></h1>'
                '<p class="hero-sub">User trip logs · Real-time from Railway MySQL · ข้อมูลถูก log อัตโนมัติทุกครั้งที่สร้างแผน</p>'
                '</div>', unsafe_allow_html=True)
with col_refresh:
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh", use_container_width=True):
        get_all_trips.clear()
        st.rerun()

# ── Load ──────────────────────────────────────────────────────────────────────
try:
    df = get_all_trips()
except Exception as e: # Catch broad exceptions first
    # Check for specific secret missing error
    err_str = str(e)
    if isinstance(e, (KeyError, SecretsMissingError)) and 'mysql' in err_str.lower():
        st.error(
            "⚠️ ไม่พบข้อมูลเชื่อมต่อ MySQL. กรุณาเพิ่มลงในไฟล์ "
            "[.streamlit/secrets.toml](/?file=/workspaces/gemma-data-driven-tourism-project/.streamlit/secrets.toml) ของคุณภายใต้ `[mysql]`"
        )
    else:
        st.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูล Trips ได้: {err_str}")
    df = pd.DataFrame() # สร้าง DataFrame ว่างเพื่อป้องกันข้อผิดพลาด

if st.session_state.get('_mysql_err'):
    st.error(f"⚠️ MySQL Error: {st.session_state['_mysql_err']}")

if df.empty:
    st.info("📭 ยังไม่มีข้อมูลแผนทริป หรือไม่สามารถเชื่อมต่อฐานข้อมูลได้ "
            "เมื่อสร้างแผนที่หน้า CitySmart Planner ระบบจะ log ข้อมูลให้อัตโนมัติ")
    st.stop()

# ── Prep ──────────────────────────────────────────────────────────────────────
df['created_at']  = pd.to_datetime(df['created_at'])
df['month']       = df['created_at'].dt.to_period('M').astype(str)
df['num_days']    = pd.to_numeric(df['num_days'],   errors='coerce')
df['travelers']   = pd.to_numeric(df['travelers'],  errors='coerce')
if 'city_type' in df.columns:
    df['city_type_th'] = df['city_type'].apply(map_city_type_th)
else:
    df['city_type_th'] = df['province'].map(_province_type_map).fillna('ไม่ทราบ')

has_budget = 'estimated_budget_thb' in df.columns and df['estimated_budget_thb'].notna().any()

# ── KPI ───────────────────────────────────────────────────────────────────────
total_trips     = len(df)
unique_provs    = df['province'].nunique()
avg_days        = round(df['num_days'].mean(), 1)
total_travelers = int(df['travelers'].sum())
avg_budget      = int(df['estimated_budget_thb'].dropna().mean()) if has_budget else None
top_province    = df['province'].value_counts().index[0]

major_pct = round((df['city_type_th'] == 'เมืองหลัก').mean() * 100)
sec_pct   = round((df['city_type_th'] == 'เมืองรอง').mean() * 100)

k1, k2, k3, k4, k5, k6 = st.columns(6)
kpi_data = [
    (k1, str(total_trips),              "แผนทริปทั้งหมด",        "",                        ""),
    (k2, str(unique_provs),             "จังหวัดที่ถูกเลือก",      f"จาก 77 จังหวัด",          "teal"),
    (k3, str(avg_days),                 "เฉลี่ยวันต่อทริป",        "วัน",                     "green"),
    (k4, f"{total_travelers:,}",        "นักท่องเที่ยวรวม",        "คน",                      "purple"),
    (k5, f"฿{avg_budget:,}" if avg_budget else "-", "งบ AI estimate เฉลี่ย", "ต่อทริป",    "orange"),
    (k6, f"{major_pct}% / {sec_pct}%", "เมืองหลัก / เมืองรอง",   f"จาก {total_trips} ทริป",  ""),
]
for col, val, label, sub, accent in kpi_data:
    col.markdown(
        f'<div class="kpi-card {accent}">'
        f'<div class="kpi-val">{val}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>', unsafe_allow_html=True
    )

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ── Insight summary ───────────────────────────────────────────────────────────
_top_ct   = df[df['province'] == top_province]['city_type_th'].iloc[0]
_ct_badge = f'<span class="badge-major">🏙️ เมืองหลัก</span>' if _top_ct == 'เมืองหลัก' else f'<span class="badge-secondary">🌿 เมืองรอง</span>'
_top_days = df[df['province'] == top_province]['num_days'].mean()
_budget_insight = f"งบ AI estimate เฉลี่ยต่อทริปอยู่ที่ <b>฿{avg_budget:,}</b>" if avg_budget else ""
st.markdown(
    f'<div class="insight-box">'
    f'<div class="insight-row">🏆 จังหวัดยอดนิยมคือ <b>{top_province}</b> {_ct_badge} · เฉลี่ย {_top_days:.1f} วันต่อทริป</div>'
    f'<div class="insight-row">🏙️ ทริปที่เลือก <b>เมืองหลัก {major_pct}%</b> &nbsp;·&nbsp; <b>เมืองรอง {sec_pct}%</b> — สะท้อน demand จริงของ users</div>'
    f'<div class="insight-row">👥 นักท่องเที่ยวรวม <b>{total_travelers:,} คน</b> ใน {total_trips} ทริป · {_budget_insight if _budget_insight else "ยังไม่มีข้อมูล AI budget"}</div>'
    f'</div>', unsafe_allow_html=True
)

st.divider()

# ── Row 1: Top Provinces + City Type donut + Budget donut ─────────────────────
col_prov, col_ct, col_bud = st.columns([2.2, 1, 1], gap="large")

with col_prov:
    st.markdown('<div class="section-label">DESTINATION</div><div class="section-title">🏆 จังหวัดยอดนิยม Top 10</div>', unsafe_allow_html=True)
    top_prov = (
        df.groupby(['province', 'city_type_th'])
        .agg(trips=('id', 'count'), avg_days=('num_days', 'mean'), travelers=('travelers', 'sum'))
        .reset_index()
        .sort_values('trips', ascending=True)
        .tail(10)
    )
    _color_map = {'เมืองหลัก': '#0077B6', 'เมืองรอง': '#FF6E40', 'ไม่ทราบ': '#CBD5E1'}
    fig_prov = go.Figure(go.Bar(
        x=top_prov['trips'],
        y=top_prov['province'],
        orientation='h',
        marker_color=[_color_map.get(ct, '#CBD5E1') for ct in top_prov['city_type_th']],
        text=[f"{r['trips']} ทริป · {r['city_type_th']}" for _, r in top_prov.iterrows()],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>%{x} ทริป<extra></extra>',
    ))
    fig_prov.update_layout(
        height=360, margin=dict(l=0, r=120, t=5, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False),
        font=dict(family='Prompt'),
    )
    # legend manual
    st.plotly_chart(fig_prov, use_container_width=True)
    st.markdown(
        '<div style="display:flex;gap:1rem;font-size:0.75rem;color:#64748b;margin-top:-0.5rem">'
        '<span>🔵 เมืองหลัก</span><span>🟠 เมืองรอง</span></div>',
        unsafe_allow_html=True
    )

with col_ct:
    st.markdown('<div class="section-label">CITY TYPE</div><div class="section-title">🏙️ สัดส่วนประเภทเมือง</div>', unsafe_allow_html=True)
    ct_count = df['city_type_th'].value_counts().reset_index()
    ct_count.columns = ['city_type_th', 'count']
    fig_ct = px.pie(
        ct_count, values='count', names='city_type_th',
        color='city_type_th',
        color_discrete_map={'เมืองหลัก': '#0077B6', 'เมืองรอง': '#FF6E40', 'ไม่ทราบ': '#CBD5E1'},
        hole=0.55,
    )
    fig_ct.update_traces(
        textinfo='percent', textfont_size=13,
        hovertemplate='<b>%{label}</b><br>%{value} ทริป (%{percent})<extra></extra>',
    )
    fig_ct.update_layout(
        height=300, margin=dict(l=0, r=0, t=5, b=45),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(orientation='h', yanchor='top', y=-0.08, xanchor='center', x=0.5, font=dict(size=11)),
        font=dict(family='Prompt'),
        annotations=[dict(
            text=f"<b>{major_pct}%</b><br><span style='font-size:10px'>หลัก</span>",
            x=0.5, y=0.5, font_size=14, showarrow=False
        )]
    )
    st.plotly_chart(fig_ct, use_container_width=True)

with col_bud:
    st.markdown('<div class="section-label">BUDGET</div><div class="section-title">💰 งบที่คนเลือก</div>', unsafe_allow_html=True)
    budget_count = df['budget'].value_counts().reset_index()
    budget_count.columns = ['budget', 'count']
    fig_budget = px.pie(
        budget_count, values='count', names='budget',
        color_discrete_sequence=['#0077B6', '#5DADE2', '#AED6F1'],
        hole=0.55,
    )
    fig_budget.update_traces(
        textinfo='percent', textfont_size=13,
        hovertemplate='<b>%{label}</b><br>%{value} ทริป (%{percent})<extra></extra>',
    )
    fig_budget.update_layout(
        height=300, margin=dict(l=0, r=0, t=5, b=45),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(orientation='h', yanchor='top', y=-0.08, xanchor='center', x=0.5, font=dict(size=11)),
        font=dict(family='Prompt'),
    )
    st.plotly_chart(fig_budget, use_container_width=True)

st.divider()

# ── Row 2: Duration (horizontal) + Time-of-day ────────────────────────────────
col_dur, col_time = st.columns(2, gap="large")

with col_dur:
    st.markdown('<div class="section-label">TRIP LENGTH</div>'
                '<div class="section-title">📅 ระยะเวลาทริปที่นิยม</div>', unsafe_allow_html=True)
    dur_count = df['num_days'].dropna().astype(int).value_counts().sort_index().reset_index()
    dur_count.columns = ['days', 'count']
    dur_count['label'] = dur_count['days'].astype(str) + ' วัน'
    dur_count['pct'] = (dur_count['count'] / dur_count['count'].sum() * 100).round(0).astype(int)
    max_count = dur_count['count'].max()
    fig_dur = go.Figure(go.Bar(
        y=dur_count['label'],
        x=dur_count['count'],
        orientation='h',
        marker_color=['#0077B6' if v == max_count else '#93C5FD' for v in dur_count['count']],
        text=[f"  {r['count']} ทริป  ({r['pct']}%)" for _, r in dur_count.iterrows()],
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=13, family='Prompt'),
        hovertemplate='%{y}: %{x} ทริป<extra></extra>',
    ))
    fig_dur.update_layout(
        height=260, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=13)),
        font=dict(family='Prompt'),
        bargap=0.25,
    )
    st.plotly_chart(fig_dur, use_container_width=True)

with col_time:
    st.markdown('<div class="section-label">PLANNING BEHAVIOR</div>'
                '<div class="section-title">🕐 ช่วงเวลาที่วางแผนทริป</div>', unsafe_allow_html=True)
    _hour = df['created_at'].dt.hour
    _bins = pd.cut(_hour, bins=[0,6,12,18,24],
                   labels=['🌙 ดึก\n(00–06)', '🌅 เช้า\n(06–12)', '☀️ บ่าย\n(12–18)', '🌆 เย็น\n(18–24)'],
                   right=False)
    _time_count = _bins.value_counts().reindex(['🌙 ดึก\n(00–06)', '🌅 เช้า\n(06–12)', '☀️ บ่าย\n(12–18)', '🌆 เย็น\n(18–24)']).fillna(0).astype(int).reset_index()
    _time_count.columns = ['period', 'count']
    _time_count['pct'] = (_time_count['count'] / _time_count['count'].sum() * 100).round(0).astype(int)
    _max_t = _time_count['count'].max()
    fig_time = go.Figure(go.Bar(
        y=_time_count['period'],
        x=_time_count['count'],
        orientation='h',
        marker_color=['#0077B6' if v == _max_t else '#93C5FD' for v in _time_count['count']],
        text=[f"  {r['count']} ทริป  ({r['pct']}%)" if r['count'] > 0 else '' for _, r in _time_count.iterrows()],
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=12, family='Prompt'),
        hovertemplate='%{y}: %{x} ทริป<extra></extra>',
    ))
    fig_time.update_layout(
        height=260, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
        font=dict(family='Prompt'),
        bargap=0.25,
    )
    st.plotly_chart(fig_time, use_container_width=True)

st.divider()

# ── Deep Dive: เมืองหลัก vs เมืองรอง metric cards + stacked bar ───────────────
st.markdown('<div class="section-label">DEEP DIVE</div>'
            '<div class="section-title">🔍 เมืองหลัก vs เมืองรอง</div>', unsafe_allow_html=True)

_ct_order = ['เมืองหลัก', 'เมืองรอง', 'ไม่ทราบ']
ct_stats = df.groupby('city_type_th').agg(
    trips=('id', 'count'),
    avg_days=('num_days', 'mean'),
    avg_travelers=('travelers', 'mean'),
).reset_index()
ct_stats['_order'] = ct_stats['city_type_th'].map({v: i for i, v in enumerate(_ct_order)})
ct_stats = ct_stats.sort_values('_order').drop(columns='_order')

# Metric comparison cards
_color_map2 = {'เมืองหลัก': '#0077B6', 'เมืองรอง': '#FF6E40', 'ไม่ทราบ': '#94a3b8'}
card_cols = st.columns(len(ct_stats) * 3)
_ci = 0
for _, row in ct_stats.iterrows():
    _c = _color_map2.get(row['city_type_th'], '#94a3b8')
    _pct_trips = round(row['trips'] / total_trips * 100)
    card_cols[_ci].markdown(
        f'<div style="background:white;border-radius:14px;padding:1rem;text-align:center;'
        f'box-shadow:0 1px 8px rgba(0,0,0,0.06);border-top:3px solid {_c};">'
        f'<div style="font-size:0.7rem;font-weight:700;color:{_c};text-transform:uppercase;letter-spacing:0.06em">{row["city_type_th"]}</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#1a1a2e;margin:0.3rem 0">{_pct_trips}%</div>'
        f'<div style="font-size:0.75rem;color:#64748b">ของทริปทั้งหมด · {row["trips"]} ทริป</div>'
        f'</div>', unsafe_allow_html=True
    )
    card_cols[_ci+1].markdown(
        f'<div style="background:white;border-radius:14px;padding:1rem;text-align:center;'
        f'box-shadow:0 1px 8px rgba(0,0,0,0.06);border-top:3px solid {_c};">'
        f'<div style="font-size:0.7rem;font-weight:700;color:{_c};text-transform:uppercase;letter-spacing:0.06em">เฉลี่ยวันเดินทาง</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#1a1a2e;margin:0.3rem 0">{row["avg_days"]:.1f}</div>'
        f'<div style="font-size:0.75rem;color:#64748b">วัน / ทริป</div>'
        f'</div>', unsafe_allow_html=True
    )
    card_cols[_ci+2].markdown(
        f'<div style="background:white;border-radius:14px;padding:1rem;text-align:center;'
        f'box-shadow:0 1px 8px rgba(0,0,0,0.06);border-top:3px solid {_c};">'
        f'<div style="font-size:0.7rem;font-weight:700;color:{_c};text-transform:uppercase;letter-spacing:0.06em">เฉลี่ยจำนวนคน</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#1a1a2e;margin:0.3rem 0">{row["avg_travelers"]:.1f}</div>'
        f'<div style="font-size:0.75rem;color:#64748b">คน / ทริป</div>'
        f'</div>', unsafe_allow_html=True
    )
    _ci += 3

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# Stacked horizontal bar: budget × city type (เมืองหลักบน เมืองรองล่าง)
ct_bud = df.groupby(['city_type_th', 'budget']).size().reset_index(name='count')
ct_bud['_order'] = ct_bud['city_type_th'].map({v: i for i, v in enumerate(_ct_order)})
ct_bud = ct_bud.sort_values('_order')

_budgets = df['budget'].value_counts().index.tolist()
_bud_colors = ['#0077B6', '#5DADE2', '#AED6F1', '#FF6E40', '#FFB347']
_y_order = [c for c in reversed(_ct_order) if c in ct_bud['city_type_th'].values]

fig_ctb = go.Figure()
for i, bud in enumerate(_budgets):
    _sub = ct_bud[ct_bud['budget'] == bud].set_index('city_type_th').reindex(_y_order).reset_index()
    fig_ctb.add_trace(go.Bar(
        name=bud,
        y=_sub['city_type_th'], x=_sub['count'],
        orientation='h',
        marker_color=_bud_colors[i % len(_bud_colors)],
        text=_sub['count'].where(_sub['count'].notna(), ''),
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=12),
        hovertemplate=f'<b>{bud}</b><br>%{{y}}: %{{x}} ทริป<extra></extra>',
    ))
fig_ctb.update_layout(
    barmode='stack',
    height=160, margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(visible=False, showgrid=False),
    yaxis=dict(showgrid=False, tickfont=dict(size=13), categoryorder='array', categoryarray=_y_order),
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='left', x=0, font=dict(size=11)),
    font=dict(family='Prompt'),
    bargap=0.3,
)
st.plotly_chart(fig_ctb, use_container_width=True)
st.caption("สัดส่วนระดับงบที่เลือก จำแนกตามประเภทเมือง")

st.divider()

# ── Sample Plans ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">SAMPLE LOGS</div><div class="section-title">📄 ตัวอย่างแผนทริปล่าสุด</div>', unsafe_allow_html=True)

top_province = df['province'].value_counts().index[0]
sample_df    = df.sort_values('created_at', ascending=False).head(5)

for _, row in sample_df.iterrows():
    _ct    = row.get('city_type_th', '')
    _ct_badge = '🏙️ เมืองหลัก' if _ct == 'เมืองหลัก' else ('🌿 เมืองรอง' if _ct == 'เมืองรอง' else '')
    _ts    = str(row['created_at'])[:16]
    _bud_val = row.get('estimated_budget_thb')
    _bud   = f"  ·  💸 ฿{int(_bud_val):,}" if pd.notna(_bud_val) and _bud_val else ""
    _loop  = f"  ·  🗺️ Loop" if row.get('loop_route') else ""
    _title = f"📍 {row['province']}  {_ct_badge}  ·  {row['trip_date']}  ·  {row['num_days']} วัน  ·  👥 {row['travelers']} คน{_bud}  ·  🕐 {_ts}{_loop}"
    with st.expander(_title):
        if row.get('loop_route'):
            st.caption(f"🗺️ เส้นทาง: {row['loop_route']}")
        st.markdown(row['itinerary'])
        if row.get('loop_highlights'):
            st.divider()
            st.markdown("**🗺️ Loop Trip Highlights**")
            st.markdown(row['loop_highlights'])

st.divider()

# ── Raw data ──────────────────────────────────────────────────────────────────
with st.expander("🗄️ ข้อมูลดิบ — Export"):
    display_df = df.drop(columns=['itinerary', 'trip_name'], errors='ignore').copy()
    st.dataframe(display_df, use_container_width=True)
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button("⬇️ Export CSV", data=csv, file_name="trip_insights_export.csv", mime="text/csv")
