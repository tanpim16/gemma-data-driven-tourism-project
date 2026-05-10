import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.mysql_connector import get_all_trips

st.set_page_config(page_title="Trip Insights", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
.block-container { padding-top: 2rem !important; }
.hero-title { font-size: 2.4rem; font-weight: 800; color: #1a1a2e; margin-bottom: -8px; }
.hero-title span { color: #0077B6; }
.hero-sub { font-size: 1rem; color: #64748b; margin-bottom: 1.5rem; }
.kpi-card {
    background: white; border-radius: 14px; padding: 1.1rem 1.3rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07); border-top: 4px solid #0077B6;
    text-align: center;
}
.kpi-val { font-size: 2rem; font-weight: 800; color: #0077B6; }
.kpi-label { font-size: 0.82rem; color: #64748b; font-weight: 600; margin-top: 2px; }
.trip-card {
    background: white; border-radius: 14px; padding: 1rem 1.3rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-left: 5px solid #0077B6;
    margin-bottom: 0.75rem;
}
.trip-title { font-size: 1rem; font-weight: 700; color: #1a1a2e; }
.trip-meta { font-size: 0.78rem; color: #64748b; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">📊 Trip <span>Insights</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">รวมข้อมูลแผนทริปที่ผู้ใช้บันทึกไว้ — วิเคราะห์จุดหมายยอดนิยม งบประมาณ และแนวโน้มการท่องเที่ยว</p>', unsafe_allow_html=True)

# ── Load data (ไม่ cache — ดึงสดจาก MySQL ทุกครั้ง) ──────────────────────────
col_refresh, _ = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

df = get_all_trips()

if df.empty:
    st.info("📭 ยังไม่มีข้อมูลแผนทริป — ไปสร้างแผนที่หน้า CitySmart Planner ระบบจะ log ข้อมูลให้อัตโนมัติ")
    st.stop()

# ── Prep ──────────────────────────────────────────────────────────────────────
df['created_at'] = pd.to_datetime(df['created_at'])
df['month']      = df['created_at'].dt.to_period('M').astype(str)
df['num_days']   = pd.to_numeric(df['num_days'], errors='coerce')
df['travelers']  = pd.to_numeric(df['travelers'], errors='coerce')

# ── KPI row ───────────────────────────────────────────────────────────────────
total_trips    = len(df)
unique_provs   = df['province'].nunique()
avg_days       = round(df['num_days'].mean(), 1)
total_travelers = int(df['travelers'].sum())

k1, k2, k3, k4 = st.columns(4)
for col, val, label in [
    (k1, total_trips,     "แผนทริปทั้งหมด"),
    (k2, unique_provs,    "จังหวัดที่สนใจ"),
    (k3, avg_days,        "เฉลี่ยวันเดินทาง"),
    (k4, f"{total_travelers:,}", "นักท่องเที่ยวรวม (คน)"),
]:
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-val">{val}</div>'
        f'<div class="kpi-label">{label}</div></div>',
        unsafe_allow_html=True
    )

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
st.divider()

# ── Row 1: Top Provinces + Budget ─────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.subheader("🏆 จังหวัดยอดนิยม")
    top_prov = (
        df.groupby('province')
        .agg(trips=('id','count'), avg_days=('num_days','mean'), travelers=('travelers','sum'))
        .reset_index()
        .sort_values('trips', ascending=True)
        .tail(10)
    )
    fig_prov = go.Figure(go.Bar(
        x=top_prov['trips'],
        y=top_prov['province'],
        orientation='h',
        marker_color='#0077B6',
        text=top_prov['trips'].astype(str) + ' ทริป',
        textposition='outside',
    ))
    fig_prov.update_layout(
        height=360, margin=dict(l=0, r=40, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_prov, use_container_width=True)

with col_right:
    st.subheader("💰 งบที่คนเลือก")
    budget_count = df['budget'].value_counts().reset_index()
    budget_count.columns = ['budget', 'count']
    fig_budget = px.pie(
        budget_count, values='count', names='budget',
        color_discrete_sequence=['#0077B6','#5DADE2','#AED6F1','#FF6E40','#FFB347'],
        hole=0.45,
    )
    fig_budget.update_traces(textinfo='label+percent', textfont_size=12)
    fig_budget.update_layout(
        height=360, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
    )
    st.plotly_chart(fig_budget, use_container_width=True)

st.divider()

# ── Row 2: Trip Duration + Trend ──────────────────────────────────────────────
col_dur, col_trend = st.columns(2, gap="large")

with col_dur:
    st.subheader("📅 ระยะเวลาทริปที่นิยม")
    dur_count = df['num_days'].dropna().astype(int).value_counts().sort_index().reset_index()
    dur_count.columns = ['days', 'count']
    dur_count['label'] = dur_count['days'].astype(str) + ' วัน'
    fig_dur = go.Figure(go.Bar(
        x=dur_count['label'], y=dur_count['count'],
        marker_color=['#0077B6' if v == dur_count['count'].max() else '#CBD5E1' for v in dur_count['count']],
        text=dur_count['count'], textposition='outside',
    ))
    fig_dur.update_layout(
        height=300, margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(visible=False, showgrid=False), xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_dur, use_container_width=True)

with col_trend:
    st.subheader("📈 แนวโน้มการบันทึกแผนทริป")
    trend = df.groupby('month').size().reset_index(name='trips')
    fig_trend = go.Figure(go.Scatter(
        x=trend['month'], y=trend['trips'],
        mode='lines+markers+text',
        text=trend['trips'], textposition='top center',
        line=dict(color='#0077B6', width=3),
        marker=dict(size=8, color='#0077B6'),
        fill='tozeroy', fillcolor='rgba(0,119,182,0.08)',
    ))
    fig_trend.update_layout(
        height=300, margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Sample Plans: most popular province ───────────────────────────────────────
st.subheader("📄 ตัวอย่างแผนทริปที่ถูกบันทึก")
top_province = df['province'].value_counts().index[0]
sample_df = df[df['province'] == top_province].head(3)

st.caption(f"แสดงตัวอย่างแผนจาก **{top_province}** (จังหวัดยอดนิยมอันดับ 1)")

for _, row in sample_df.iterrows():
    _ts = str(row['created_at'])[:16]
    with st.expander(f"📍 {row['province']}  ·  {row['trip_date']}  |  {row['num_days']} วัน  |  👥 {row['travelers']} คน  |  🕐 {_ts}"):
        st.markdown(row['itinerary'])

st.divider()

# ── Raw table (internal) ───────────────────────────────────────────────────────
with st.expander("🗄️ ข้อมูลดิบ (Internal — สำหรับทำรีพอร์ต)"):
    display_df = df.drop(columns=['itinerary', 'trip_name'], errors='ignore').copy()
    st.dataframe(display_df, use_container_width=True)
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "⬇️ Export CSV", data=csv,
        file_name="trip_insights_export.csv", mime="text/csv"
    )
