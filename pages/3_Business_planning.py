import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ─── 1. Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CitySmart Business Planner",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── 2. CSS Styling (Clean & Seamless) ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Prompt', sans-serif !important;
}

.stApp {
    background: #f8fafc;
}

:root { --main-font-size: 1.2rem; }

/* หัวข้อและคำบรรยาย */
.hero-title { font-size: 2.8rem; font-weight: 800; color: #1a1a2e; margin-bottom: -10px; }
.hero-title span { color: #0077B6; }
.hero-subtitle { font-size: 1.3rem; color: #64748b; margin-bottom: 2rem; }

/* ปรับแต่ง Selectbox */
.stSelectbox label p { font-size: var(--main-font-size) !important; font-weight: 600 !important; color: #1e293b; }

/* ส่วนกล่องบทวิเคราะห์ (แบบไม่มีพื้นหลังสีขาว) */
.insight-box, .strategy-box {
    font-size: var(--main-font-size) !important;
    line-height: 1.6; 
    padding: 1rem 0; 
    margin-top: 5px;
    border-top: 1px solid #e2e8f0;
}
.insight-box { color: #0f172a; border-left: 5px solid #0077B6; padding-left: 15px; }
.strategy-box { color: #475569; }

/* ลบช่องว่างส่วนเกิน */
.block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; }
.stMarkdownContainer p { margin-bottom: 0px !important; }
</style>
""", unsafe_allow_html=True)

# ─── 3. Data Loading Functions ───────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        # 1. โหลดข้อมูลท่องเที่ยว
        df_load = pd.read_csv('data/master_tourism_analysis.csv')
        # ปรับปี พ.ศ. เป็น ค.ศ.
        df_load['Year'] = df_load['Year'].apply(lambda x: x - 543 if x > 2500 else x)
        
        month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 
                     'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        df_load['Month_Num'] = df_load['Month'].map(month_map)
        df_load['YearMonth'] = pd.to_datetime(df_load['Year'].astype(str) + '-' + df_load['Month_Num'].astype(str).str.zfill(2) + '-01')
        
        # 2. โหลดข้อมูล Google Trends
        trends_df = pd.read_csv('data/Google_Trends_Data.csv')
        trends_df['Month_Num'] = trends_df['Month'].map(month_map)
        year_col = 'Year_AD' if 'Year_AD' in trends_df.columns else 'Year'
        trends_df['date'] = pd.to_datetime(trends_df[year_col].astype(str) + '-' + trends_df['Month_Num'].astype(str).str.zfill(2) + '-01')
        trends_agg = trends_df.groupby(['ProvinceThai', 'date'])['Search_Interest'].sum().reset_index()
        trends_agg.rename(columns={'Search_Interest': 'Combined_Search'}, inplace=True)
        
        return df_load, trends_agg
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

df, all_trends_df = load_data()

# ─── 4. UI Section ───────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">💼 Business <span>Planning</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">วิเคราะห์ข้อมูลย้อนหลังและยอดพยากรณ์เพื่อเตรียมแผนธุรกิจ</p>', unsafe_allow_html=True)

if not df.empty:
    available_provinces = sorted(df['ProvinceThai'].dropna().unique())
    selected_province = st.selectbox("📍 เลือกจังหวัดเพื่อเริ่มวิเคราะห์", options=available_provinces, index=0)
else:
    selected_province = None
    st.error("ไม่สามารถโหลดข้อมูลได้ กรุณาตรวจสอบโฟลเดอร์ data และไฟล์ CSV")

st.write("---")

# ─── 5. Analysis Section ─────────────────────────────────────────────────────
if selected_province:
    prov_data = df[df['ProvinceThai'] == selected_province]
    prov_trends = all_trends_df[all_trends_df['ProvinceThai'] == selected_province]
    
    if not prov_data.empty:
        city_type_th = prov_data['City_type_TH'].iloc[0]
        city_type_en = prov_data['City_type_EN'].iloc[0]
        lag_val = 1 if city_type_en == 'Major City' else 2

        # ─── 5.1 Historical Graph (2023-2025) ───
        st.subheader("📊 ข้อมูลย้อนหลัง (Historical Data)")
        hist_df = prov_data[prov_data['Year'].isin([2023, 2024, 2025])].sort_values('YearMonth')
        
        fig_hist = make_subplots(specs=[[{"secondary_y": True}]])
        fig_hist.add_trace(go.Scatter(x=hist_df['YearMonth'], y=hist_df['total_visitors'], name="นักท่องเที่ยวจริง", mode='lines+markers', line=dict(color='#0077B6', width=3)), secondary_y=False)
        
        hist_trends = prov_trends[(prov_trends['date'].dt.year >= 2023) & (prov_trends['date'].dt.year <= 2025)]
        if not hist_trends.empty:
            fig_hist.add_trace(go.Scatter(x=hist_trends['date'], y=hist_trends['Combined_Search'], name="การค้นหาบน Google", mode='lines', line=dict(color='#FF6E40', dash='dot')), secondary_y=True)
        
        fig_hist.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=1.1, x=1))
        st.plotly_chart(fig_hist, use_container_width=True)

        st.write("---")

        # ─── 5.2 Forecast Graph (2026) with Auto-Projection ───
        st.subheader("🔮 การคาดการณ์ปี 2026 (Forecast)")
        
        # ค้นหาข้อมูลปี 2026
        pred_df = prov_data[prov_data['Year'] == 2026].sort_values('Month_Num')
        
        # ระบบพยากรณ์อัตโนมัติกรณีไม่มีข้อมูลปี 2026
        is_simulated = False
        if pred_df.empty:
            data_2025 = prov_data[prov_data['Year'] == 2025].sort_values('Month_Num')
            if not data_2025.empty:
                pred_df = data_2025.copy()
                pred_df['Year'] = 2026
                pred_df['total_visitors'] = pred_df['total_visitors'] * 1.10 # คาดการณ์โต 10%
                is_simulated = True

        if not pred_df.empty:
            if is_simulated:
                st.caption("⚠️ หมายเหตุ: แสดงข้อมูลคาดการณ์ Growth +10% จากปีฐาน 2025")
            
            fig_2026 = make_subplots(specs=[[{"secondary_y": True}]])
            
            # จำนวนนักท่องเที่ยว (Bar)
            fig_2026.add_trace(go.Bar(
                x=pred_df['Month'], y=pred_df['total_visitors'], 
                name="คาดการณ์นักท่องเที่ยว", marker_color='#0077B6', opacity=0.6
            ), secondary_y=False)
            
            # แนวโน้มการค้นหา (Line)
            pred_trends = prov_trends[prov_trends['date'].dt.year == 2026].sort_values('date')
            if pred_trends.empty: # ถ้าไม่มี Trends 2026 ให้ใช้ Pattern ของ 2025 มาเทียบ
                pred_trends = prov_trends[prov_trends['date'].dt.year == 2025].sort_values('date')
            
            if not pred_trends.empty:
                fig_2026.add_trace(go.Scatter(
                    x=pred_df['Month'], y=pred_trends['Combined_Search'], 
                    name="แนวโน้มการค้นหา", mode='lines+markers', 
                    line=dict(color='#FF6E40', width=3)
                ), secondary_y=True)
            
            fig_2026.update_layout(
                height=400, margin=dict(l=0, r=0, t=20, b=0), 
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False), legend=dict(orientation="h", y=1.1, x=1)
            )
            st.plotly_chart(fig_2026, use_container_width=True)
        else:
            st.warning("ไม่สามารถสร้างการพยากรณ์ได้ เนื่องจากไม่พบข้อมูลปี 2025/2026")

        # ─── 5.3 Insight Box ───
        st.markdown(f"""
        <div class="insight-box">
            <strong>📝 บทวิเคราะห์สำหรับจังหวัด {selected_province}:</strong><br>
            จากการวิเคราะห์พบว่าจังหวัดนี้เป็น <b>{city_type_th}</b> ซึ่งมี <b>Lag Time {lag_val} เดือน</b><br>
            กลยุทธ์ที่แนะนำ: เมื่อเห็นเส้นพยากรณ์การค้นหา (สีส้ม) เริ่มสูงขึ้น คุณต้องเริ่มแคมเปญการตลาดทันทีล่วงหน้าอย่างน้อย {lag_val} เดือน
        </div>
        <div class="strategy-box">
            📌 <b>Business Tip:</b> ใช้ช่วงเวลา {lag_val} เดือนก่อน High Season ในการจอง Media หรือทำโปรโมชั่น Early Bird เพื่อดึงลูกค้าก่อนคู่แข่ง
        </div>
        """, unsafe_allow_html=True)