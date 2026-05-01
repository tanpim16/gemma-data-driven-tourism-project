import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="CitySmart | Market Analysis", page_icon="📈", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
        .block-container { padding-top: 1.5rem; }
        .city-badge {
            display: inline-block; padding: 4px 14px; border-radius: 20px;
            font-size: 13px; font-weight: 600; color: white;
        }
        .gap-metric {
            border-radius: 14px; padding: 1rem 1.1rem; border-left: 5px solid;
            background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.06); height: 100%;
        }
        .gap-metric .gm-label { font-size: 0.78rem; font-weight: 600; color: #777; margin-bottom: 0.3rem; }
        .gap-metric .gm-value { font-size: 1.35rem; font-weight: 800; line-height: 1.2; margin-bottom: 0.15rem; }
        .gap-metric .gm-sub   { font-size: 0.73rem; color: #888; margin-top: 0.1rem; }
        .gap-metric.sev-ok    { border-left-color: #27ae60; background: #f0faf4; }
        .gap-metric.sev-warn  { border-left-color: #f39c12; background: #fffbf0; }
        .gap-metric.sev-crit  { border-left-color: #e74c3c; background: #fff5f5; }
        .gap-metric.sev-info  { border-left-color: #2980b9; background: #f0f6ff; }
        .section-summary {
            background: #f8f9fa; border-radius: 10px; padding: 0.55rem 1rem;
            font-size: 0.85rem; color: #555; margin-bottom: 0.7rem;
            border-left: 3px solid #2980b9;
        }
        .insight-callout {
            border-left: 4px solid #1a73e8; background: #f0f7ff;
            border-radius: 0 8px 8px 0; padding: 0.5rem 1rem;
            margin: 0.3rem 0 0.9rem 0; font-size: 0.83rem; color: #333;
        }
        .viewing-banner {
            background: linear-gradient(135deg, #1E3D59 0%, #2980b9 100%);
            border-radius: 10px; padding: 0.55rem 1.2rem; color: white;
            font-size: 0.88rem; margin-bottom: 0.8rem;
        }
    </style>
""", unsafe_allow_html=True)

# ── Color constants (consistent across all charts) ────────────────────────────
C_NAVY   = '#1E3D59'   # เมืองหลัก / คนไทย
C_SKY    = '#5DADE2'   # เมืองรอง / ต่างชาติ (ฟ้าอ่อน)
C_CORAL  = '#FF6E40'   # badge / severity accent
C_GREEN  = '#27ae60'
C_AMBER  = '#f39c12'
C_RED    = '#e74c3c'
CITY_COLORS    = {'Major City': C_NAVY, 'Secondary City': C_SKY}
VISITOR_COLORS = {'🇹🇭 คนไทย': C_NAVY, '✈️ ต่างชาติ': C_SKY}
YEAR_COLORS    = {'2566': C_NAVY, '2567': C_SKY, '2568': C_GREEN}

MONTH_ORDER  = list(range(1, 13))
MONTH_LABELS = {1:'ม.ค.',2:'ก.พ.',3:'มี.ค.',4:'เม.ย.',5:'พ.ค.',6:'มิ.ย.',
                7:'ก.ค.',8:'ส.ค.',9:'ก.ย.',10:'ต.ค.',11:'พ.ย.',12:'ธ.ค.'}
MONTH_ENG_MAP = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
                 'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}


# ── Helper functions ──────────────────────────────────────────────────────────
def _gap_severity(value, warn_thresh, crit_thresh):
    if value >= crit_thresh: return 'sev-crit', C_RED
    if value >= warn_thresh: return 'sev-warn', C_AMBER
    return 'sev-ok', C_GREEN

def metric_card(label, value_str, sub_str, value_color=C_NAVY, sev_class='sev-info'):
    return (
        f'<div class="gap-metric {sev_class}">'
        f'<div class="gm-label">{label}</div>'
        f'<div class="gm-value" style="color:{value_color};">{value_str}</div>'
        f'<div class="gm-sub">{sub_str}</div>'
        f'</div>'
    )

def section_summary(text):
    st.markdown(f'<div class="section-summary">{text}</div>', unsafe_allow_html=True)

def insight_box(df, value_col, group_col=None, year_col=None, unit='ล้านบาท'):
    """Render auto-insight below a chart: max/min, YoY%."""
    if df.empty or value_col not in df.columns:
        return
    v = df[value_col]
    max_idx, min_idx = v.idxmax(), v.idxmin()
    max_lbl = (f" <span style='color:#555;font-size:0.8rem'>({df.loc[max_idx, group_col]})</span>"
               if group_col and group_col in df.columns else "")
    min_lbl = (f" <span style='color:#555;font-size:0.8rem'>({df.loc[min_idx, group_col]})</span>"
               if group_col and group_col in df.columns else "")
    parts = [
        f"<span style='color:#1a73e8;font-weight:700'>📈 สูงสุด</span>"
        f" <b>{v[max_idx]:,.0f}</b> {unit}{max_lbl}",
        f"<span style='color:#e74c3c;font-weight:700'>📉 ต่ำสุด</span>"
        f" <b>{v[min_idx]:,.0f}</b> {unit}{min_lbl}",
    ]
    if year_col and year_col in df.columns:
        years = sorted(df[year_col].unique())
        if len(years) >= 2:
            latest = df[df[year_col] == years[-1]][value_col].sum()
            prev   = df[df[year_col] == years[-2]][value_col].sum()
            if prev > 0:
                pct   = (latest - prev) / prev * 100
                color = '#27ae60' if pct >= 0 else '#e74c3c'
                arrow = '↑' if pct >= 0 else '↓'
                parts.append(
                    f"<span style='color:{color};font-weight:700'>"
                    f"{arrow} YoY ({years[-2]}→{years[-1]})</span> <b>{pct:+.1f}%</b>"
                )
    st.markdown(
        '<div class="insight-callout">' + '&nbsp;&nbsp;·&nbsp;&nbsp;'.join(parts) + '</div>',
        unsafe_allow_html=True
    )


@st.cache_data
def load_data():
    try:
        df_t  = pd.read_csv('data/master_tourism_analysis.csv')
        df_f  = pd.read_excel('data/Thailand_Festival_Master.xlsx')
        df_fe = pd.read_csv('data/Thailand_Festival_With_Events.csv')
        return df_t.dropna(subset=['ProvinceEN']), df_f, df_fe
    except FileNotFoundError as e:
        st.error(f"ไม่พบไฟล์ข้อมูล: {e}"); st.stop()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}"); st.stop()


df_tour, df_fest, df_fest_events = load_data()
df_tour = df_tour[df_tour['City_type_EN'].isin(['Major City', 'Secondary City'])].copy()

# Build province mapping early (needed by sidebar)
prov_map = (
    df_tour[['ProvinceThai', 'ProvinceEN']].drop_duplicates()
    .dropna(subset=['ProvinceThai', 'ProvinceEN'])
    .set_index('ProvinceThai')['ProvinceEN'].to_dict()
)
prov_thai_sorted = sorted(prov_map.keys())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.caption("📊 ข้อมูล: กระทรวงการท่องเที่ยวฯ 2566–2568")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#1E3D59;margin-bottom:2px;'>📈 Market Analysis</h2>",
            unsafe_allow_html=True)
st.caption("เจาะลึกสถิติการท่องเที่ยวทั่วไทย 3 ปี (2566–2568) · 76 จังหวัด · 21 เมืองหลัก · 55 เมืองรอง")

tab_national, tab_province, tab_festival = st.tabs([
    "🌐 ภาพรวมประเทศ", "📍 รายจังหวัด", "🎪 เทศกาลทั่วไทย",
])

# ══════════════════════════════════════════════════════════════════════════════
# Tab 1: National Overview
# ══════════════════════════════════════════════════════════════════════════════
with tab_national:
    st.write("")

    # Pre-compute aggregations
    summary = df_tour.groupby('City_type_EN').agg(
        total_revenue   =('total_revenue',   'sum'),
        avg_revenue     =('total_revenue',   'mean'),
        avg_occupancy   =('occupancy_rate',  'mean'),
        total_visitors  =('total_visitors',  'sum'),
        thai_revenue    =('thai_revenue',    'sum'),
        foreign_revenue =('foreign_revenue', 'sum'),
    ).reset_index()

    yearly_by_type = df_tour.groupby(['Year', 'City_type_EN'])['total_revenue'].sum().reset_index()
    avg_by_type    = yearly_by_type.groupby('City_type_EN')['total_revenue'].mean()

    major     = summary[summary['City_type_EN'] == 'Major City']
    secondary = summary[summary['City_type_EN'] == 'Secondary City']

    # ── Section 1: KPI Cards ──────────────────────────────────────────────────
    st.markdown("#### 📊 ช่องว่างเมืองหลัก vs เมืองรอง")

    if not major.empty and not secondary.empty:
        maj = major.iloc[0]
        sec = secondary.iloc[0]
        maj_avg_yr = avg_by_type.get('Major City', 0)
        sec_avg_yr = avg_by_type.get('Secondary City', 0)
        gap_ratio  = maj['avg_revenue'] / sec['avg_revenue'] if sec['avg_revenue'] > 0 else 0
        occ_diff   = maj['avg_occupancy'] - sec['avg_occupancy']

        section_summary(
            f"เมืองหลักสร้างรายได้เฉลี่ย <b>{maj_avg_yr/1e6:.2f} ล้านล้านบาท/ปี</b> "
            f"สูงกว่าเมืองรอง <b>{gap_ratio:.1f} เท่า</b> "
            f"· ช่องว่างอัตราเข้าพักอยู่ที่ <b>{abs(occ_diff):.1f}%</b>"
        )

        gap_cls, gap_col = _gap_severity(gap_ratio, warn_thresh=3, crit_thresh=7)
        occ_cls, occ_col = _gap_severity(abs(occ_diff), warn_thresh=5, crit_thresh=15)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(metric_card(
                "💰 รายได้รวม เมืองหลัก",
                f"{maj_avg_yr/1_000_000:.2f}",
                "ล้านล้านบาท · เฉลี่ยต่อปี", C_NAVY, 'sev-info'
            ), unsafe_allow_html=True)
        with m2:
            st.markdown(metric_card(
                "💰 รายได้รวม เมืองรอง",
                f"{sec_avg_yr/1_000_000:.2f}",
                "ล้านล้านบาท · เฉลี่ยต่อปี", C_CORAL, 'sev-info'
            ), unsafe_allow_html=True)
        with m3:
            st.markdown(metric_card(
                "📉 ช่องว่างรายได้เฉลี่ย",
                f"{gap_ratio:.1f}×",
                f"เมืองหลักสูงกว่าเมืองรอง "
                f"{'⚠️ วิกฤต' if gap_ratio >= 7 else '⚠️ สูง' if gap_ratio >= 3 else '✅ พอรับได้'}",
                gap_col, gap_cls
            ), unsafe_allow_html=True)
        with m4:
            st.markdown(metric_card(
                "🏨 ช่องว่างอัตราเข้าพัก",
                f"{abs(occ_diff):.1f}%",
                f"เมืองหลักสูงกว่า "
                f"{'⚠️ วิกฤต' if abs(occ_diff) >= 15 else '⚠️ สูง' if abs(occ_diff) >= 5 else '✅ ใกล้เคียง'}",
                occ_col, occ_cls
            ), unsafe_allow_html=True)

    st.write("")

    # ── Section 2: Revenue split ──────────────────────────────────────────────
    c1, c2 = st.columns([1, 1.2])

    with c1:
        if not major.empty and not secondary.empty:
            maj_pct = maj['total_revenue'] / (maj['total_revenue'] + sec['total_revenue']) * 100
        else:
            maj_pct = 0
        total_rev_all = summary['total_revenue'].sum()
        st.markdown(f"#### เมืองหลักครอง {maj_pct:.0f}% ของรายได้ทั้งประเทศ")
        section_summary(
            f"รายได้สะสม 3 ปีรวมกัน <b>{total_rev_all/1e6:.2f} ล้านล้านบาท</b> "
            f"· เมืองรองมีศักยภาพที่ยังไม่ถูกดึงออกมา"
        )
        fig_p = px.pie(
            summary, values='total_revenue', names='City_type_EN', hole=0.58,
            color='City_type_EN', color_discrete_map=CITY_COLORS,
        )
        fig_p.update_traces(textposition='inside', textinfo='percent+label')
        fig_p.update_layout(
            showlegend=False, margin=dict(t=10, b=10, l=0, r=0),
            annotations=[dict(
                text=f"<b>{total_rev_all/1e6:.2f}</b><br><span style='font-size:11px'>ล้านล้านบาท</span>",
                x=0.5, y=0.5, font_size=15, showarrow=False, font=dict(color=C_NAVY),
            )]
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with c2:
        # Compute YoY for insight title
        yoy_df = yearly_by_type[yearly_by_type['City_type_EN'] == 'Major City'].sort_values('Year')
        if len(yoy_df) >= 2:
            yoy_pct = (yoy_df.iloc[-1]['total_revenue'] - yoy_df.iloc[-2]['total_revenue']) / \
                       yoy_df.iloc[-2]['total_revenue'] * 100
            yoy_arrow = "เพิ่มขึ้น" if yoy_pct >= 0 else "ลดลง"
            yoy_title = f"รายได้เมืองหลัก{yoy_arrow} {abs(yoy_pct):.1f}% ใน {int(yoy_df.iloc[-1]['Year'])}"
        else:
            yoy_title = "เปรียบเทียบรายได้แยกปี"
        st.markdown(f"#### {yoy_title}")
        section_summary("แยกรายได้เมืองหลัก (navy) vs เมืองรอง (ส้ม) ในแต่ละปีงบประมาณ")

        yearly_plot = yearly_by_type.copy()
        yearly_plot['label'] = yearly_plot['total_revenue'].apply(
            lambda x: f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.1f}K"
        )
        fig_yr = px.bar(
            yearly_plot, x='Year', y='total_revenue', color='City_type_EN',
            barmode='group', text='label', color_discrete_map=CITY_COLORS,
        )
        fig_yr.update_traces(textposition='outside')
        fig_yr.update_layout(
            yaxis_title="ล้านบาท", xaxis_title="ปี",
            legend_title="ประเภทเมือง", margin=dict(t=30, b=0)
        )
        st.plotly_chart(fig_yr, use_container_width=True)
        insight_box(yearly_by_type, 'total_revenue', group_col='City_type_EN',
                    year_col='Year', unit='ล้านบาท')

    # ── Section 3: Occupancy by region ───────────────────────────────────────
    st.markdown("#### 🏨 ภูมิภาคไหนช่องว่างอัตราเข้าพักสูงสุด?")
    region_data = (
        df_tour.dropna(subset=['Region_EN'])
        .groupby(['Region_EN', 'City_type_EN'])['occupancy_rate']
        .mean().reset_index()
    )
    # Find region with largest gap
    region_pivot = region_data.pivot(index='Region_EN', columns='City_type_EN', values='occupancy_rate').dropna()
    if not region_pivot.empty and 'Major City' in region_pivot.columns and 'Secondary City' in region_pivot.columns:
        region_pivot['gap'] = region_pivot['Major City'] - region_pivot['Secondary City']
        worst_region = region_pivot['gap'].idxmax()
        worst_gap = region_pivot['gap'].max()
        section_summary(
            f"ช่องว่างสูงสุดอยู่ที่ <b>{worst_region}</b> "
            f"ซึ่งเมืองหลักมีอัตราเข้าพักสูงกว่าเมืองรองถึง <b>{worst_gap:.1f}%</b>"
        )

    fig_reg = px.bar(
        region_data, x='Region_EN', y='occupancy_rate', color='City_type_EN',
        barmode='group', text_auto='.1f', color_discrete_map=CITY_COLORS,
    )
    fig_reg.update_layout(
        xaxis_title="ภูมิภาค", yaxis_title="อัตราเข้าพัก (%)",
        legend_title="ประเภทเมือง", margin=dict(t=20, b=0), plot_bgcolor='white',
        yaxis=dict(gridcolor='#eee'),
    )
    st.plotly_chart(fig_reg, use_container_width=True)
    insight_box(region_data, 'occupancy_rate', group_col='Region_EN', unit='%')

    # ── Section 4: Thai vs Foreign ────────────────────────────────────────────
    tf_nat = (
        df_tour.groupby(['Year', 'City_type_EN'])
        [['thai_revenue', 'foreign_revenue', 'thai_visitors', 'foreign_visitors']]
        .sum().reset_index()
    )
    tf_nat['Year'] = tf_nat['Year'].astype(str)

    # Compute foreign % for insight title
    total_thai    = tf_nat['thai_revenue'].sum()
    total_foreign = tf_nat['foreign_revenue'].sum()
    foreign_pct   = total_foreign / (total_thai + total_foreign) * 100 if (total_thai + total_foreign) > 0 else 0

    # Check if foreign % changed in latest year
    nat_yr = tf_nat.groupby('Year')[['thai_revenue', 'foreign_revenue']].sum()
    nat_yr['foreign_pct'] = nat_yr['foreign_revenue'] / (nat_yr['thai_revenue'] + nat_yr['foreign_revenue']) * 100
    years_sorted = sorted(nat_yr.index)
    if len(years_sorted) >= 2:
        fpct_latest = nat_yr.loc[years_sorted[-1], 'foreign_pct']
        fpct_prev   = nat_yr.loc[years_sorted[-2], 'foreign_pct']
        fpct_dir    = "เพิ่มขึ้น" if fpct_latest > fpct_prev else "ลดลง"
        tf_title = (
            f"ต่างชาติสร้างรายได้ {foreign_pct:.0f}% ของทั้งหมด "
            f"· สัดส่วน{fpct_dir}ใน {years_sorted[-1]}"
        )
    else:
        tf_title = f"ต่างชาติสร้างรายได้ {foreign_pct:.0f}% ของรายได้ทั้งหมด"

    st.markdown(f"#### 🌏 {tf_title}")
    section_summary(
        f"คนไทย (navy) และต่างชาติ (ส้ม) สร้างรายได้ในสัดส่วน "
        f"<b>{100-foreign_pct:.0f}%:{foreign_pct:.0f}%</b> "
        f"· แยกตามเมืองหลัก/รอง และปีงบประมาณ"
    )

    tf_melt = tf_nat.melt(
        id_vars=['Year', 'City_type_EN'],
        value_vars=['thai_revenue', 'foreign_revenue'],
        var_name='ประเภท', value_name='รายได้'
    )
    tf_melt['ประเภท'] = tf_melt['ประเภท'].map(
        {'thai_revenue': '🇹🇭 คนไทย', 'foreign_revenue': '✈️ ต่างชาติ'}
    )
    tf_melt['label'] = tf_melt['รายได้'].apply(
        lambda x: f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}K" if x >= 1e3 else f"{x:.0f}"
    )
    fig_tf = px.bar(
        tf_melt, x='Year', y='รายได้', color='ประเภท', text='label',
        barmode='stack', facet_col='City_type_EN',
        color_discrete_map=VISITOR_COLORS,
        labels={'รายได้': 'รายได้ (ล้านบาท)', 'Year': 'ปี'},
        category_orders={'City_type_EN': ['Major City', 'Secondary City']},
    )
    fig_tf.update_traces(
        textposition='outside',
        textfont=dict(size=10, color='#333'), marker_line_width=0,
    )
    fig_tf.update_layout(
        legend_title='ประเภทนักท่องเที่ยว', margin=dict(t=40, b=20),
        plot_bgcolor='white', yaxis=dict(gridcolor='#eee'),
        uniformtext_minsize=8, uniformtext_mode='hide',
    )
    fig_tf.for_each_annotation(lambda a: a.update(
        text=a.text.replace('City_type_EN=Major City', '🏙️ เมืองหลัก')
                   .replace('City_type_EN=Secondary City', '🌿 เมืองรอง')
    ))
    st.plotly_chart(fig_tf, use_container_width=True)

    tf_for_insight = tf_nat[['Year', 'thai_revenue', 'foreign_revenue']].groupby('Year').sum().reset_index()
    tf_for_insight['total'] = tf_for_insight['thai_revenue'] + tf_for_insight['foreign_revenue']
    insight_box(tf_for_insight, 'foreign_revenue', group_col='Year',
                year_col='Year', unit='ล้านบาท (ต่างชาติ)')

    # ── Section 5: Visitor counts (2 rows × 3 cols) ───────────────────────────
    st.divider()
    st.markdown("#### 👥 จำนวนนักท่องเที่ยวสะสม 3 ปี")
    section_summary("แสดงจำนวนสะสมทุกจังหวัดและทุกเดือนตลอด 3 ปีงบประมาณ (หน่วย: ล้านคน)")
    vis_nat = df_tour.groupby('City_type_EN')[['total_visitors', 'thai_visitors', 'foreign_visitors']].sum()
    vis_cards = [
        ('Major City',     'total_visitors',   '🏙️ นักท่องเที่ยวรวม', 'เมืองหลัก'),
        ('Major City',     'thai_visitors',    '🇹🇭 คนไทย',           'เมืองหลัก'),
        ('Major City',     'foreign_visitors', '✈️ ต่างชาติ',          'เมืองหลัก'),
        ('Secondary City', 'total_visitors',   '🌿 นักท่องเที่ยวรวม', 'เมืองรอง'),
        ('Secondary City', 'thai_visitors',    '🇹🇭 คนไทย',           'เมืองรอง'),
        ('Secondary City', 'foreign_visitors', '✈️ ต่างชาติ',          'เมืองรอง'),
    ]
    for row_cards in [vis_cards[:3], vis_cards[3:]]:
        cols = st.columns(3)
        for col, (city, key, label, sublabel) in zip(cols, row_cards):
            if city in vis_nat.index:
                val = vis_nat.loc[city, key]
                col.markdown(
                    metric_card(f"{label}", f"{val/1e6:.1f}M", f"ล้านคน · {sublabel}",
                                C_NAVY if city == 'Major City' else C_SKY, 'sev-info'),
                    unsafe_allow_html=True
                )
        st.write("")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2: Province Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
with tab_province:
    # ── Filters (province + year) ─────────────────────────────────────────────
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        selected_province_th = st.selectbox("🔍 คุณกำลังสนใจจังหวัดไหน?", prov_thai_sorted)
        selected_province    = prov_map[selected_province_th]
        st.session_state['selected_province'] = selected_province
    with col_f2:
        year_opts     = ['ทุกปี'] + sorted(df_tour['Year'].unique().tolist(), reverse=True)
        selected_year = st.selectbox("📅 ปี", year_opts)

    # Viewing banner
    st.markdown(
        f'<div class="viewing-banner">📍 กำลังดูข้อมูล: '
        f'<b>{selected_province_th}</b> · ปี <b>{selected_year}</b></div>',
        unsafe_allow_html=True
    )

    p_df = df_tour[df_tour['ProvinceEN'] == selected_province].copy()
    p_df['spend'] = (p_df['total_revenue'] * 1_000_000) / p_df['total_visitors'].replace(0, 1)

    city_type   = p_df['City_type_EN'].iloc[0] if not p_df.empty else 'Unknown'
    badge_color = C_NAVY if city_type == 'Major City' else C_CORAL
    badge_label = "🏙️ เมืองหลัก" if city_type == 'Major City' else "🌿 เมืองรอง"
    st.markdown(
        f'<span class="city-badge" style="background:{badge_color}">{badge_label}</span>',
        unsafe_allow_html=True
    )
    st.write("")

    # ── KPI row ───────────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💸 ใช้จ่ายต่อหัวเฉลี่ย",    f"{p_df['spend'].mean():,.0f} บาท")
    m2.metric("👥 นักท่องเที่ยวรวม/เดือน", f"{p_df['total_visitors'].mean():,.0f} คน")
    m3.metric("🇹🇭 คนไทย/เดือน",           f"{p_df['thai_visitors'].mean():,.0f} คน")
    m4.metric("✈️ ต่างชาติ/เดือน",          f"{p_df['foreign_visitors'].mean():,.0f} คน")
    m5.metric("🏨 อัตราเข้าพักเฉลี่ย",      f"{p_df['occupancy_rate'].mean():.1f}%")

    # YoY growth card
    yearly_rev = p_df.groupby('Year')['total_revenue'].sum().reset_index().sort_values('Year')
    if len(yearly_rev) >= 2:
        latest = yearly_rev.iloc[-1]
        prev   = yearly_rev.iloc[-2]
        growth = ((latest['total_revenue'] - prev['total_revenue']) / prev['total_revenue'] * 100
                  if prev['total_revenue'] > 0 else 0)
        st.metric(
            f"📈 รายได้รวมปี {int(latest['Year'])} เทียบ {int(prev['Year'])}",
            f"{latest['total_revenue']:,.0f} ล้านบาท",
            delta=f"{growth:+.1f}%"
        )

    st.write("")

    # Filter by year
    plot_df = (p_df if selected_year == 'ทุกปี'
               else p_df[p_df['Year'] == int(selected_year)]).copy()

    plot_df['month_num']   = plot_df['Month'].map(MONTH_ENG_MAP)
    plot_df['month_label'] = plot_df['month_num'].map(MONTH_LABELS)
    plot_df['Year']        = plot_df['Year'].astype(str)
    plot_df = plot_df.dropna(subset=['month_num']).sort_values('month_num')
    ordered_labels = [MONTH_LABELS[m] for m in MONTH_ORDER if m in plot_df['month_num'].values]

    # ── Monthly revenue Heatmap ───────────────────────────────────────────────
    if not plot_df.empty:
        best_month_idx = plot_df.groupby('month_label')['total_revenue'].mean().idxmax()
        rev_title = (
            f"🔥 {best_month_idx} คือ High Season ของ {selected_province_th}"
            f"<br><sup style='color:#888;font-weight:400;font-size:11px'>"
            f"รายได้รายเดือน (ล้านบาท) · น้ำเงินเข้ม = รายได้สูง</sup>"
        )
    else:
        rev_title = f"รายได้รายเดือน {selected_province_th}"

    section_summary(
        f"น้ำเงินเข้ม = High Season (รายได้สูง) · น้ำเงินอ่อน = Low Season · "
        f"อ่านแนวนอนเพื่อดู Seasonality, อ่านแนวตั้งเพื่อดูการเติบโตรายปี"
    )

    heat_prov = (
        plot_df.groupby(['Year', 'month_label'])['total_revenue'].sum().reset_index()
    )
    heat_pivot = (
        heat_prov.pivot(index='Year', columns='month_label', values='total_revenue')
        .reindex(columns=ordered_labels)
    )

    HEATMAP_SCALE = [
        [0.0, '#D6EAF8'],   # น้ำเงินอ่อน — Low Season
        [1.0, '#1E3D59'],   # น้ำเงินเข้ม — High Season / ขุมทรัพย์
    ]
    fig_rev = go.Figure(data=go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=[str(y) for y in heat_pivot.index.tolist()],
        colorscale=HEATMAP_SCALE,
        text=heat_pivot.values,
        texttemplate='%{text:,.0f}',
        textfont=dict(size=11),
        hovertemplate='ปี %{y} · %{x}<br>รายได้: <b>%{z:,.0f}</b> ล้านบาท<extra></extra>',
        colorbar=dict(title='ล้านบาท', thickness=14),
    ))
    fig_rev.update_layout(
        title=dict(text=rev_title, font=dict(size=14, color='#1E3D59'), x=0),
        xaxis_title='เดือน', yaxis_title='ปี',
        margin=dict(t=55, b=20, l=60, r=20),
        height=max(180, 80 * len(heat_pivot)),
        paper_bgcolor='#fafafa', plot_bgcolor='#fafafa',
    )
    with st.container():
        st.plotly_chart(fig_rev, use_container_width=True)
        insight_box(plot_df, 'total_revenue', group_col='month_label',
                    year_col='Year', unit='ล้านบาท')
    st.write("")

    # ── Thai vs Foreign by month ──────────────────────────────────────────────
    prov_thai_rev    = plot_df['thai_revenue'].sum()
    prov_foreign_rev = plot_df['foreign_revenue'].sum()
    prov_total_rev   = prov_thai_rev + prov_foreign_rev
    prov_foreign_pct = prov_foreign_rev / prov_total_rev * 100 if prov_total_rev > 0 else 0

    st.markdown(f"#### 🌏 ต่างชาติสร้างรายได้ {prov_foreign_pct:.0f}% ใน {selected_province_th}")
    section_summary(
        f"คนไทย (น้ำเงินเข้ม) vs ต่างชาติ (น้ำเงินอ่อน) รายเดือน "
        f"· สัดส่วนต่างชาติ <b>{prov_foreign_pct:.0f}%</b> "
        f"· ใช้วางแผนกลยุทธ์ดึงดูดนักท่องเที่ยวกลุ่มเป้าหมาย"
    )
    years_in_plot = sorted(plot_df['Year'].unique())
    tf_prov = plot_df.melt(
        id_vars=['month_label', 'Year', 'month_num'],
        value_vars=['thai_revenue', 'foreign_revenue'],
        var_name='ประเภท', value_name='รายได้'
    )
    tf_prov['ประเภท'] = tf_prov['ประเภท'].map(
        {'thai_revenue': '🇹🇭 คนไทย', 'foreign_revenue': '✈️ ต่างชาติ'}
    )
    tf_prov['ประเภท'] = pd.Categorical(
        tf_prov['ประเภท'], categories=['🇹🇭 คนไทย', '✈️ ต่างชาติ'], ordered=True
    )
    tf_prov['label'] = tf_prov['รายได้'].apply(
        lambda x: f"{x:,.0f}" if x >= 50 else ""
    )
    tf_title = (
        f"คนไทย {100-prov_foreign_pct:.0f}% vs ต่างชาติ {prov_foreign_pct:.0f}% — {selected_province_th}"
        f"<br><sup style='color:#888;font-weight:400;font-size:11px'>"
        f"รายได้รายเดือน (ล้านบาท) · น้ำเงินเข้ม = คนไทย · น้ำเงินอ่อน = ต่างชาติ</sup>"
    )
    BLUE_VISITOR_COLORS = {'🇹🇭 คนไทย': '#1E3D59', '✈️ ต่างชาติ': '#85C1E9'}
    fig_tf_p = px.bar(
        tf_prov, x='month_label', y='รายได้', color='ประเภท', text='label',
        barmode='stack',
        facet_col='Year' if len(years_in_plot) > 1 else None,
        color_discrete_map=BLUE_VISITOR_COLORS,
        category_orders={
            'month_label': ordered_labels,
            'ประเภท': ['🇹🇭 คนไทย', '✈️ ต่างชาติ'],
        },
        labels={'รายได้': 'ล้านบาท', 'month_label': 'เดือน'},
    )
    fig_tf_p.update_traces(
        marker_line_width=0,
        textposition='inside',
        textfont=dict(size=10, color='white'),
        insidetextanchor='middle',
    )
    fig_tf_p.update_layout(
        title=dict(text=tf_title, font=dict(size=14, color='#1E3D59'), x=0),
        legend_title='ประเภท', bargap=0.18,
        paper_bgcolor='#fafafa', plot_bgcolor='#fafafa',
        yaxis=dict(gridcolor='#e0e0e0', gridwidth=0.5),
        margin=dict(t=55, b=0),
    )
    with st.container():
        st.plotly_chart(fig_tf_p, use_container_width=True)
        st.caption("หน่วย: ล้านบาท · ตัวเลขในแท่งกราฟแสดงรายได้ของแต่ละกลุ่มนักท่องเที่ยว")
        insight_box(
            plot_df[['month_label', 'foreign_revenue', 'thai_revenue']],
            'foreign_revenue', group_col='month_label', unit='ล้านบาท (ต่างชาติ)'
        )

    # ── Festival section ──────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"#### 📅 เทศกาลที่น่าสนใจใน {selected_province_th}")
    fe_list = df_fest_events[df_fest_events['Province_ID'] == selected_province].copy()
    f_list  = df_fest[df_fest['Province_ID'] == selected_province]

    if not fe_list.empty:
        show_cols  = [c for c in ['Festival_Name_TH','Festival_Name_EN','Month','Season','Category']
                      if c in fe_list.columns]
        rename_map = {
            'Festival_Name_TH':'ชื่อเทศกาล (ไทย)', 'Festival_Name_EN':'ชื่อเทศกาล (ENG)',
            'Month':'เดือน', 'Season':'ฤดูกาล', 'Category':'หมวดหมู่',
        }
        st.dataframe(fe_list[show_cols].rename(columns=rename_map),
                     use_container_width=True, hide_index=True)
    elif not f_list.empty:
        cols = st.columns(min(len(f_list), 3))
        impact_colors = {'High': C_GREEN, 'Medium': C_AMBER, 'Low': '#7f8c8d'}
        for i, (_, row) in enumerate(f_list.iterrows()):
            with cols[i % 3]:
                ic = impact_colors.get(str(row.get('Economic_Impact', '')), '#7f8c8d')
                st.markdown(
                    f"**{row['Festival_Name_TH']}**  \n"
                    f"🗓️ เดือน {row['Month']} | "
                    f"<span style='color:{ic}'>● {row.get('Economic_Impact','-')} Impact</span>",
                    unsafe_allow_html=True
                )
    else:
        st.caption("ยังไม่มีข้อมูลเทศกาลในจังหวัดนี้")


# ══════════════════════════════════════════════════════════════════════════════
# Tab 3: Festival Master Dataset
# ══════════════════════════════════════════════════════════════════════════════
with tab_festival:
    st.write("")
    st.markdown("#### 🎪 ฐานข้อมูลเทศกาลทั่วประเทศไทย")
    section_summary(
        f"ครอบคลุม <b>{len(df_fest_events):,} รายการ</b> จาก "
        f"{df_fest_events['Province_ID'].nunique()} จังหวัด "
        f"· กรองตามภูมิภาค หมวดหมู่ หรือฤดูกาลได้ด้านล่าง"
    )

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        regions    = ['ทั้งหมด'] + sorted(df_fest_events['Region'].dropna().unique().tolist())
        f_region   = st.selectbox("กรองตามภูมิภาค", regions)
    with fc2:
        categories = ['ทั้งหมด'] + sorted(df_fest_events['Category'].dropna().unique().tolist())
        f_cat      = st.selectbox("กรองตามหมวดหมู่", categories)
    with fc3:
        seasons    = ['ทั้งหมด'] + sorted(df_fest_events['Season'].dropna().unique().tolist())
        f_season   = st.selectbox("กรองตามฤดูกาล", seasons)

    filt = df_fest_events.copy()
    if f_region != 'ทั้งหมด': filt = filt[filt['Region']   == f_region]
    if f_cat    != 'ทั้งหมด': filt = filt[filt['Category'] == f_cat]
    if f_season != 'ทั้งหมด': filt = filt[filt['Season']   == f_season]

    st.write(f"แสดง **{len(filt):,}** รายการ")
    display_cols = [c for c in
                    ['Province_ID','Festival_Name_TH','Festival_Name_EN','Month','Region','Season','Category']
                    if c in filt.columns]
    rename_map = {
        'Province_ID':'จังหวัด', 'Festival_Name_TH':'ชื่อเทศกาล (ไทย)',
        'Festival_Name_EN':'ชื่อเทศกาล (ENG)', 'Month':'เดือน',
        'Region':'ภูมิภาค', 'Season':'ฤดูกาล', 'Category':'หมวดหมู่',
    }
    st.dataframe(filt[display_cols].rename(columns=rename_map),
                 use_container_width=True, hide_index=True)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    st.write("")
    st.markdown("#### 🌡️ Hotspot เทศกาล — ภูมิภาค × หมวดหมู่")
    section_summary("ความเข้มของสี = จำนวนเทศกาล · เซลล์สีเข้ม = ภูมิภาคที่โดดเด่นในหมวดนั้น")

    heat_df = (
        df_fest_events.dropna(subset=['Region', 'Category'])
        .groupby(['Region', 'Category']).size().reset_index(name='count')
    )
    pivot = heat_df.pivot(index='Region', columns='Category', values='count').fillna(0).astype(int)
    fig_heat = go.Figure(data=go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale='YlOrRd', text=pivot.values, texttemplate='%{text}',
        textfont=dict(size=12, color='#333'),
        hovertemplate='ภูมิภาค: %{y}<br>หมวดหมู่: %{x}<br>จำนวน: %{z}<extra></extra>',
        showscale=True, colorbar=dict(title='จำนวน'),
    ))
    fig_heat.update_layout(
        xaxis_title='หมวดหมู่เทศกาล', yaxis_title='ภูมิภาค',
        margin=dict(t=20, b=60, l=80, r=20), plot_bgcolor='white', height=320,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Top cell insight
    flat = heat_df.loc[heat_df['count'].idxmax()]
    st.info(f"📈 **Hotspot สูงสุด:** {flat['Region']} × {flat['Category']} "
            f"มีเทศกาลถึง **{flat['count']} รายการ**")

    # ── Treemap ───────────────────────────────────────────────────────────────
    st.markdown("#### 🌳 สัดส่วนหมวดหมู่เทศกาลทั่วประเทศ")
    section_summary("ขนาดกล่อง = จำนวนเทศกาล · หมวดหมู่ไหนกล่องใหญ่ = ครองสัดส่วนมากที่สุดทั่วประเทศ")
    treemap_df = (
        df_fest_events.dropna(subset=['Category', 'Region'])
        .groupby(['Category', 'Region']).size().reset_index(name='count')
    )
    top_cat = treemap_df.groupby('Category')['count'].sum().idxmax()
    fig_tree = px.treemap(
        treemap_df, path=['Category', 'Region'], values='count',
        color='count', color_continuous_scale='Blues', hover_data={'count': True},
    )
    fig_tree.update_traces(
        textinfo='label+value',
        hovertemplate='<b>%{label}</b><br>จำนวน: %{value}<extra></extra>',
    )
    fig_tree.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=380)
    st.plotly_chart(fig_tree, use_container_width=True)
    st.info(f"🏆 **หมวดหมู่ที่มีเทศกาลมากที่สุด:** {top_cat} "
            f"({treemap_df.groupby('Category')['count'].sum()[top_cat]} รายการทั่วประเทศ)")
