import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CitySmart | Market Analysis", page_icon="📈", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; }
        .city-badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    try:
        df_t = pd.read_csv('data/master_tourism_analysis.csv')
        df_f = pd.read_excel('data/Thailand_Festival_Master.xlsx')
        df_fe = pd.read_csv('data/Thailand_Festival_With_Events.csv')
        return df_t.dropna(subset=['ProvinceEN']), df_f, df_fe
    except FileNotFoundError as e:
        st.error(f"ไม่พบไฟล์ข้อมูล: {e}")
        st.stop()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        st.stop()


df_tour, df_fest, df_fest_events = load_data()
df_tour = df_tour[df_tour['City_type_EN'].isin(['Major City', 'Secondary City'])].copy()

st.markdown("<h2 style='color: #1E3D59;'>📈 Market Analysis</h2>", unsafe_allow_html=True)
st.write("เจาะลึกสถิติการท่องเที่ยวทั่วไทย 3 ปี (2566–2568) เพื่อค้นหาโอกาสและช่องว่างในทุกจังหวัด")

tab_national, tab_province, tab_festival = st.tabs([
    "🌐 ภาพรวมประเทศ",
    "📍 รายจังหวัด",
    "🎪 เทศกาลทั่วไทย",
])

# ── Tab 1: National Overview ──────────────────────────────────────────────────
with tab_national:
    st.write("")
    summary = df_tour.groupby('City_type_EN').agg(
        total_revenue=('total_revenue', 'sum'),
        avg_revenue=('total_revenue', 'mean'),
        avg_occupancy=('occupancy_rate', 'mean'),
        total_visitors=('total_visitors', 'sum'),
    ).reset_index()

    major = summary[summary['City_type_EN'] == 'Major City']
    secondary = summary[summary['City_type_EN'] == 'Secondary City']

    if not major.empty and not secondary.empty:
        maj = major.iloc[0]
        sec = secondary.iloc[0]
        gap_ratio = maj['avg_revenue'] / sec['avg_revenue'] if sec['avg_revenue'] > 0 else 0
        occ_diff = maj['avg_occupancy'] - sec['avg_occupancy']

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 รายได้รวม เมืองหลัก", f"{maj['total_revenue']:,.0f} ล้าน")
        m2.metric("💰 รายได้รวม เมืองรอง", f"{sec['total_revenue']:,.0f} ล้าน")
        m3.metric("📉 ช่องว่างรายได้เฉลี่ย", f"{gap_ratio:.1f}×",
                  delta=f"เมืองหลักสูงกว่า {gap_ratio:.1f} เท่า", delta_color="off")
        m4.metric("🏨 ช่องว่างอัตราเข้าพัก", f"{abs(occ_diff):.1f}%",
                  delta=f"เมืองหลักสูงกว่า {occ_diff:+.1f}%", delta_color="inverse")

    st.write("")
    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.markdown("#### สัดส่วนรายได้รวม (ทุกปี)")
        fig_p = px.pie(
            summary, values='total_revenue', names='City_type_EN', hole=0.55,
            color='City_type_EN',
            color_discrete_map={'Major City': '#1E3D59', 'Secondary City': '#FF6E40'},
        )
        fig_p.update_traces(textposition='inside', textinfo='percent+label')
        fig_p.update_layout(showlegend=False, margin=dict(t=10, b=10, l=0, r=0))
        st.plotly_chart(fig_p, use_container_width=True)
        st.caption("เมืองหลัก (น้ำเงิน) vs เมืองรอง (ส้ม)")

    with c2:
        st.markdown("#### เปรียบเทียบรายได้แยกปี")
        yearly = df_tour.groupby(['Year', 'City_type_EN'])['total_revenue'].sum().reset_index()
        fig_yr = px.bar(
            yearly, x='Year', y='total_revenue', color='City_type_EN',
            barmode='group', text_auto='.0f',
            color_discrete_map={'Major City': '#1E3D59', 'Secondary City': '#FF6E40'},
        )
        fig_yr.update_layout(
            yaxis_title="ล้านบาท", xaxis_title="ปี",
            legend_title="ประเภทเมือง", margin=dict(t=20, b=0)
        )
        st.plotly_chart(fig_yr, use_container_width=True)

    st.markdown("#### อัตราการเข้าพักเฉลี่ยแยกตามภูมิภาค")
    region_data = (
        df_tour.dropna(subset=['Region_EN'])
        .groupby(['Region_EN', 'City_type_EN'])['occupancy_rate']
        .mean()
        .reset_index()
    )
    fig_reg = px.bar(
        region_data, x='Region_EN', y='occupancy_rate', color='City_type_EN',
        barmode='group', text_auto='.1f',
        color_discrete_map={'Major City': '#1E3D59', 'Secondary City': '#FF6E40'},
    )
    fig_reg.update_layout(
        xaxis_title="ภูมิภาค", yaxis_title="อัตราเข้าพัก (%)",
        legend_title="ประเภทเมือง", margin=dict(t=20, b=0)
    )
    st.plotly_chart(fig_reg, use_container_width=True)

# ── Tab 2: Province Deep Dive ─────────────────────────────────────────────────
with tab_province:
    st.write("")
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        selected_province = st.selectbox(
            "คุณกำลังสนใจจังหวัดไหน?", sorted(df_tour['ProvinceEN'].unique())
        )
        st.session_state['selected_province'] = selected_province
    with col_f2:
        year_opts = ['ทุกปี'] + sorted(df_tour['Year'].unique().tolist(), reverse=True)
        selected_year = st.selectbox("เลือกปี", year_opts)

    p_df = df_tour[df_tour['ProvinceEN'] == selected_province].copy()
    p_df['spend'] = (p_df['total_revenue'] * 1_000_000) / p_df['total_visitors'].replace(0, 1)

    city_type = p_df['City_type_EN'].iloc[0] if not p_df.empty else 'Unknown'
    badge_color = "#1E3D59" if city_type == 'Major City' else "#FF6E40"
    badge_label = "🏙️ เมืองหลัก" if city_type == 'Major City' else "🌿 เมืองรอง"
    st.markdown(
        f'<span class="city-badge" style="background:{badge_color}">{badge_label}</span>',
        unsafe_allow_html=True
    )
    st.write("")

    m1, m2, m3 = st.columns(3)
    m1.metric("ยอดใช้จ่ายต่อหัวเฉลี่ย", f"{p_df['spend'].mean():,.0f} บาท")
    m2.metric("นักท่องเที่ยวเฉลี่ย/เดือน", f"{p_df['total_visitors'].mean():,.0f} คน")
    m3.metric("อัตราเข้าพักเฉลี่ย", f"{p_df['occupancy_rate'].mean():.1f}%")

    # YoY growth
    yearly_rev = p_df.groupby('Year')['total_revenue'].sum().reset_index().sort_values('Year')
    if len(yearly_rev) >= 2:
        latest = yearly_rev.iloc[-1]
        prev = yearly_rev.iloc[-2]
        growth = ((latest['total_revenue'] - prev['total_revenue']) / prev['total_revenue'] * 100
                  if prev['total_revenue'] > 0 else 0)
        st.metric(
            f"การเติบโตของรายได้ ปี {latest['Year']} เทียบ {prev['Year']}",
            f"{latest['total_revenue']:,.0f} ล้านบาท",
            delta=f"{growth:+.1f}%"
        )

    st.write("")
    plot_df = p_df if selected_year == 'ทุกปี' else p_df[p_df['Year'] == int(selected_year)]
    fig_rev = px.bar(
        plot_df, x='Month', y='total_revenue', color='Year', barmode='group',
        title=f"รายได้จากการท่องเที่ยวรายเดือน: {selected_province}",
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig_rev.update_layout(yaxis_title="ล้านบาท", xaxis_title="เดือน")
    st.plotly_chart(fig_rev, use_container_width=True)

    st.divider()
    st.markdown(f"#### 📅 เทศกาลที่น่าสนใจใน {selected_province}")

    fe_list = df_fest_events[df_fest_events['Province_ID'] == selected_province].copy()
    f_list = df_fest[df_fest['Province_ID'] == selected_province]

    if not fe_list.empty:
        show_cols = [c for c in ['Festival_Name_TH', 'Festival_Name_EN', 'Month', 'Season', 'Category']
                     if c in fe_list.columns]
        rename_map = {
            'Festival_Name_TH': 'ชื่อเทศกาล (ไทย)', 'Festival_Name_EN': 'ชื่อเทศกาล (ENG)',
            'Month': 'เดือน', 'Season': 'ฤดูกาล', 'Category': 'หมวดหมู่',
        }
        st.dataframe(
            fe_list[show_cols].rename(columns=rename_map),
            use_container_width=True, hide_index=True
        )
    elif not f_list.empty:
        cols = st.columns(min(len(f_list), 3))
        impact_colors = {'High': '#27ae60', 'Medium': '#f39c12', 'Low': '#7f8c8d'}
        for i, (_, row) in enumerate(f_list.iterrows()):
            with cols[i % 3]:
                ic = impact_colors.get(str(row.get('Economic_Impact', '')), '#7f8c8d')
                st.markdown(
                    f"**{row['Festival_Name_TH']}**  \n"
                    f"🗓️ เดือน {row['Month']} | "
                    f"<span style='color:{ic}'>● {row.get('Economic_Impact', '-')} Impact</span>",
                    unsafe_allow_html=True
                )
    else:
        st.caption("ยังไม่มีข้อมูลเทศกาลในจังหวัดนี้")

# ── Tab 3: Festival Master Dataset ───────────────────────────────────────────
with tab_festival:
    st.write("")
    st.markdown("#### 🎪 ฐานข้อมูลเทศกาลทั่วประเทศไทย")
    st.write(f"ครอบคลุม **{len(df_fest_events):,}** รายการ จาก {df_fest_events['Province_ID'].nunique()} จังหวัด")

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        regions = ['ทั้งหมด'] + sorted(df_fest_events['Region'].dropna().unique().tolist())
        f_region = st.selectbox("กรองตามภูมิภาค", regions)
    with fc2:
        categories = ['ทั้งหมด'] + sorted(df_fest_events['Category'].dropna().unique().tolist())
        f_cat = st.selectbox("กรองตามหมวดหมู่", categories)
    with fc3:
        seasons = ['ทั้งหมด'] + sorted(df_fest_events['Season'].dropna().unique().tolist())
        f_season = st.selectbox("กรองตามฤดูกาล", seasons)

    filt = df_fest_events.copy()
    if f_region != 'ทั้งหมด':
        filt = filt[filt['Region'] == f_region]
    if f_cat != 'ทั้งหมด':
        filt = filt[filt['Category'] == f_cat]
    if f_season != 'ทั้งหมด':
        filt = filt[filt['Season'] == f_season]

    st.write(f"แสดง **{len(filt):,}** รายการ")

    display_cols = [c for c in
                    ['Province_ID', 'Festival_Name_TH', 'Festival_Name_EN', 'Month', 'Region', 'Season', 'Category']
                    if c in filt.columns]
    rename_map = {
        'Province_ID': 'จังหวัด', 'Festival_Name_TH': 'ชื่อเทศกาล (ไทย)',
        'Festival_Name_EN': 'ชื่อเทศกาล (ENG)', 'Month': 'เดือน',
        'Region': 'ภูมิภาค', 'Season': 'ฤดูกาล', 'Category': 'หมวดหมู่',
    }
    st.dataframe(
        filt[display_cols].rename(columns=rename_map),
        use_container_width=True, hide_index=True
    )

    st.write("")
    st.markdown("#### การกระจายตัวของเทศกาลตามภูมิภาคและหมวดหมู่")
    cat_region = (
        df_fest_events.dropna(subset=['Region', 'Category'])
        .groupby(['Region', 'Category'])
        .size()
        .reset_index(name='จำนวน')
    )
    fig_cat = px.bar(
        cat_region, x='Region', y='จำนวน', color='Category',
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_cat.update_layout(
        xaxis_title="ภูมิภาค", yaxis_title="จำนวนเทศกาล", legend_title="หมวดหมู่"
    )
    st.plotly_chart(fig_cat, use_container_width=True)
