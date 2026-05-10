import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.snowflake_connector import query_snowflake

# ─── 1. Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CitySmart Business Planner",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
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
        # 1. โหลดข้อมูลท่องเที่ยวจาก Snowflake
        df_load = query_snowflake("SELECT * FROM TOURISM_DB.PUBLIC.TOURISM_STATS")
        # Snowflake คืน UPPERCASE columns → remap
        _remap = {
            'YEAR': 'Year', 'MONTH': 'Month', 'PROVINCETHAI': 'ProvinceThai',
            'PROVINCEEN': 'ProvinceEN', 'REGION_TH': 'Region_TH', 'REGION_EN': 'Region_EN',
            'CITY_TYPE_TH': 'City_type_TH', 'CITY_TYPE_EN': 'City_type_EN',
            'PRICE_INDEX': 'Price_Index', 'NO': 'No',
        }
        df_load.columns = [_remap.get(c, c.lower()) for c in df_load.columns]
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
    except Exception as e:
        st.error(f"โหลดข้อมูลไม่สำเร็จ: {e}")
        return pd.DataFrame(), pd.DataFrame()

def calc_lag(visitors_series, trends_series, fallback=1, max_lag=6):
    v = visitors_series.reset_index(drop=True)
    t = trends_series.reset_index(drop=True)
    min_len = min(len(v), len(t))
    if min_len < 4:
        return fallback
    v, t = v.iloc[:min_len], t.iloc[:min_len]
    v_norm = (v - v.mean()) / (v.std() + 1e-9)
    t_norm = (t - t.mean()) / (t.std() + 1e-9)
    best_lag, best_corr = 0, -999
    for lag in range(0, max_lag + 1):
        corr = v_norm.iloc[lag:].corr(t_norm.iloc[:-lag]) if lag > 0 else v_norm.corr(t_norm)
        if corr > best_corr:
            best_corr, best_lag = corr, lag
    return best_lag

def calc_yoy_growth(df_prov):
    yearly = df_prov.groupby('Year')['total_visitors'].sum()
    growths = []
    for y in [2023, 2024]:
        if y in yearly.index and (y + 1) in yearly.index and yearly[y] > 0:
            growths.append((yearly[y + 1] - yearly[y]) / yearly[y])
    return sum(growths) / len(growths) if growths else 0.10

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

        # ─── คำนวณ Lag จากข้อมูลจริงด้วย cross-correlation ───
        _fallback_lag = 1 if city_type_en == 'Major City' else 2
        if not prov_trends.empty:
            merged = pd.merge(
                prov_data[['YearMonth', 'total_visitors']],
                prov_trends.rename(columns={'date': 'YearMonth'}),
                on='YearMonth', how='inner'
            ).sort_values('YearMonth')
            lag_val = calc_lag(merged['total_visitors'], merged['Combined_Search'], fallback=_fallback_lag)
        else:
            lag_val = _fallback_lag

        # ─── คำนวณ YoY Growth (ใช้ทุกครั้ง ไม่ขึ้นกับว่า 2026 มีข้อมูลจริงหรือไม่) ───
        yoy_rate = calc_yoy_growth(prov_data)
        yoy_pct  = round(yoy_rate * 100, 1)

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
                pred_df['total_visitors'] = (pred_df['total_visitors'] * (1 + yoy_rate)).round().astype(int)
                pred_df['YearMonth'] = pd.to_datetime('2026-' + pred_df['Month_Num'].astype(str).str.zfill(2) + '-01')
                is_simulated = True

        if not pred_df.empty:
            if is_simulated:
                st.caption(f"⚠️ หมายเหตุ: แสดงข้อมูลคาดการณ์ Growth {'+' if yoy_pct >= 0 else ''}{yoy_pct}% (เฉลี่ย YoY จริง) จากปีฐาน 2025")

            fig_2026 = make_subplots(specs=[[{"secondary_y": True}]])

            # จำนวนนักท่องเที่ยว (Bar) — ใช้ YearMonth (date) เป็น x เพื่อให้ align กับ Trends ได้ถูกต้อง
            fig_2026.add_trace(go.Bar(
                x=pred_df['YearMonth'], y=pred_df['total_visitors'],
                name="คาดการณ์นักท่องเที่ยว", marker_color='#0077B6', opacity=0.6
            ), secondary_y=False)

            # แนวโน้มการค้นหา (Line) — align ด้วย date เดียวกัน
            pred_trends = prov_trends[prov_trends['date'].dt.year == 2026].sort_values('date')
            if pred_trends.empty:
                pred_trends = prov_trends[prov_trends['date'].dt.year == 2025].sort_values('date').copy()
                pred_trends['date'] = pred_trends['date'] + pd.DateOffset(years=1)

            if not pred_trends.empty:
                fig_2026.add_trace(go.Scatter(
                    x=pred_trends['date'], y=pred_trends['Combined_Search'],
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

        # ─── 5.3 Peak Month Analysis ───
        st.write("---")
        st.subheader("📅 เดือนที่นักท่องเที่ยวสูงสุด (Peak Months)")

        month_names = {1:'ม.ค.', 2:'ก.พ.', 3:'มี.ค.', 4:'เม.ย.', 5:'พ.ค.', 6:'มิ.ย.',
                       7:'ก.ค.', 8:'ส.ค.', 9:'ก.ย.', 10:'ต.ค.', 11:'พ.ย.', 12:'ธ.ค.'}
        month_avg = (
            prov_data[prov_data['Year'].isin([2023, 2024, 2025])]
            .groupby('Month_Num')['total_visitors']
            .mean()
            .reindex(range(1, 13), fill_value=0)  # เรียง ม.ค.–ธ.ค. เสมอ
        )
        peak_months = month_avg.nlargest(3).index.tolist()
        peak_labels = ', '.join(month_names[m] for m in sorted(peak_months))

        bar_colors = ['#0077B6' if m in peak_months else '#CBD5E1' for m in month_avg.index]

        fig_peak = go.Figure(go.Bar(
            x=[month_names[m] for m in month_avg.index],
            y=month_avg.values,
            marker_color=bar_colors,
            text=[f"{int(v/1000)}K" if v >= 1000 else str(int(v)) for v in month_avg.values],
            textposition='outside',
            textfont=dict(size=12, color=['#0077B6' if m in peak_months else '#94a3b8' for m in month_avg.index]),
        ))
        fig_peak.update_layout(
            height=320, margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=False, visible=False),
            xaxis=dict(showgrid=False),
            uniformtext_minsize=10, uniformtext_mode='hide',
        )
        st.plotly_chart(fig_peak, use_container_width=True)
        st.caption(f"🔵 Peak: {peak_labels}  (เฉลี่ยจากปี 2023–2025)")

        st.write("---")

        # ─── 5.4 Insight Box ───
        # คำนวณเดือนที่ควรเริ่มแคมเปญ (peak month แรก - lag)
        first_peak_month = sorted(peak_months)[0]
        campaign_month_num = ((first_peak_month - lag_val - 1) % 12) + 1
        campaign_month_label = month_names[campaign_month_num]
        growth_sign = '+' if yoy_pct >= 0 else ''

        st.markdown(f"""
        <div class="insight-box">
            <strong>📝 บทวิเคราะห์สำหรับจังหวัด {selected_province}:</strong><br>
            จังหวัดนี้เป็น <b>{city_type_th}</b> · ช่วง Peak คือ <b>{peak_labels}</b>
            · YoY Growth เฉลี่ย <b>{growth_sign}{yoy_pct}%</b> · Lag Time <b>{lag_val} เดือน</b><br>
            เมื่อเห็นกราฟการค้นหา (เส้นส้ม) เริ่มสูงขึ้น ให้เริ่มแคมเปญล่วงหน้าทันที อย่างน้อย {lag_val} เดือน
        </div>
        <div class="strategy-box">
            📌 <b>Business Tip:</b> เริ่มจอง Media / ทำ Early Bird ตั้งแต่ <b>{campaign_month_label}</b>
            เพื่อเข้าถึงลูกค้าก่อนที่ Peak ({peak_labels}) จะมาถึง
        </div>
        """, unsafe_allow_html=True)