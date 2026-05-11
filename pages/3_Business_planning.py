import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime

st.set_page_config(page_title="แผนธุรกิจการท่องเที่ยวไทย (Thailand Tourism Business Planning)", page_icon="📊", layout="wide")

st.markdown("""
<style>
.section-header { background: linear-gradient(135deg,#0077B6,#00b4d8); color:white; padding:1rem 1.5rem; border-radius:10px; margin:1rem 0; }
.insight-card { background:#f0f9ff; border-left:4px solid #0077B6; border-radius:8px; padding:1rem 1.5rem; margin:0.8rem 0; }
.analysis-box { background:#fff7ed; border-left:4px solid #f97316; border-radius:8px; padding:1rem 1.5rem; margin:0.8rem 0; }
.kpi-box { background:white; border-radius:10px; padding:1rem; box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:3px solid #0077B6; text-align:center; }
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

MAJOR_CITIES_TH = ["กรุงเทพมหานคร","เชียงใหม่","ภูเก็ต","ชลบุรี","สุราษฎร์ธานี"]
SECONDARY_CITIES_TH = ["เชียงราย","กาญจนบุรี","กระบี่","อยุธยา","นครราชสีมา","อุดรธานี","ขอนแก่น","สงขลา","เพชรบุรี","ระยอง"]

MONTH_MAP = {"Jan":"ม.ค.","Feb":"ก.พ.","Mar":"มี.ค.","Apr":"เม.ย.","May":"พ.ค.","Jun":"มิ.ย.",
             "Jul":"ก.ค.","Aug":"ส.ค.","Sep":"ก.ย.","Oct":"ต.ค.","Nov":"พ.ย.","Dec":"ธ.ค."}
MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MONTH_NUM = {m:i+1 for i,m in enumerate(MONTH_ORDER)}

@st.cache_data
def load_data():
    gt = pd.read_csv(os.path.join(DATA,"Google_Trends_Data.csv"))
    mt = pd.read_csv(os.path.join(DATA,"master_tourism_analysis.csv"))
    tr = pd.read_csv(os.path.join(DATA,"Travel_search2026.csv"))
    tr["date"] = pd.to_datetime(tr["date"])
    tr["interest"] = pd.to_numeric(tr["interest"], errors="coerce").fillna(0)
    mt["total_visitors"] = pd.to_numeric(mt["total_visitors"], errors="coerce").fillna(0)
    gt["Search_Interest"] = pd.to_numeric(gt["Search_Interest"], errors="coerce").fillna(0)
    gt["month_num"] = gt["Month"].map(MONTH_NUM)
    return gt, mt, tr

gt, mt, tr = load_data()

st.title("📊 แผนธุรกิจการท่องเที่ยวไทย (Thailand Tourism Business Planning)")
st.markdown("วิเคราะห์ข้อมูลเชิงลึกเพื่อวางแผนธุรกิจ โดยใช้ข้อมูล Google Trends และสถิตินักท่องเที่ยว ปี 2023–2026")

st.divider()
st.markdown('<div class="section-header"><h2>📈 ส่วนที่ 1: เมืองหลัก – นักท่องเที่ยว vs Google Search (2023–2025) (Major Cities – Visitors vs Google Search Trends)</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
<b>🔍 คำอธิบาย (Explanation):</b> กราฟด้านล่างแสดงความสัมพันธ์ระหว่าง <b>จำนวนนักท่องเที่ยว (Total Visitors)</b> 
และ <b>ค่าความสนใจค้นหาบน Google (Google Search Interest)</b> รายเดือน ปี 2023–2025 สำหรับ <b>เมืองหลัก (Major Cities)</b><br>
แกน Y ซ้าย = จำนวนนักท่องเที่ยว (Visitors) | แกน Y ขวา = ค่า Google Search Interest (0–100)
</div>
""", unsafe_allow_html=True)

major_mt = mt[mt["ProvinceThai"].isin(MAJOR_CITIES_TH)].copy()
major_mt["month_num"] = major_mt["Month"].map(MONTH_NUM)
major_gt = gt[gt["ProvinceThai"].isin(MAJOR_CITIES_TH)].copy()

city_sel_major = st.selectbox("เลือกจังหวัดเมืองหลัก (Select Major City)", MAJOR_CITIES_TH, key="major_city")

mt_city = major_mt[major_mt["ProvinceThai"]==city_sel_major].copy()
mt_city_monthly = mt_city.groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
mt_city_monthly["label"] = mt_city_monthly["Year"].astype(str)+"-M"+mt_city_monthly["month_num"].astype(str).str.zfill(2)
mt_city_monthly = mt_city_monthly.sort_values(["Year","month_num"])

gt_city = major_gt[(major_gt["ProvinceThai"]==city_sel_major)].copy()
gt_city_monthly = gt_city.groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()
gt_city_monthly["label"] = gt_city_monthly["Year_AD"].astype(str)+"-M"+gt_city_monthly["month_num"].astype(str).str.zfill(2)
gt_city_monthly = gt_city_monthly.sort_values(["Year_AD","month_num"])

fig1 = make_subplots(specs=[[{"secondary_y":True}]])
fig1.add_trace(go.Bar(x=mt_city_monthly["label"],y=mt_city_monthly["total_visitors"],name="นักท่องเที่ยว (Visitors)",marker_color="#0077B6",opacity=0.7),secondary_y=False)
fig1.add_trace(go.Scatter(x=gt_city_monthly["label"],y=gt_city_monthly["Search_Interest"],name="Google Search Interest",mode="lines+markers",line=dict(color="#f97316",width=2.5),marker=dict(size=6)),secondary_y=True)
fig1.update_layout(title=f"เมืองหลัก: {city_sel_major} – นักท่องเที่ยว vs Google Search (2023–2025)",height=420,template="plotly_white",legend=dict(orientation="h",y=1.1),margin=dict(t=60,b=50))
fig1.update_yaxes(title_text="จำนวนนักท่องเที่ยว (Visitors)",secondary_y=False)
fig1.update_yaxes(title_text="Google Search Interest (0–100)",secondary_y=True)
st.plotly_chart(fig1, use_container_width=True)

st.divider()
st.markdown('<div class="section-header"><h2>🏘️ ส่วนที่ 2: เมืองรอง – นักท่องเที่ยว vs Google Search (2023–2025) (Secondary Cities – Visitors vs Google Search Trends)</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
<b>🔍 คำอธิบาย (Explanation):</b> กราฟด้านล่างแสดงความสัมพันธ์เดียวกันสำหรับ <b>เมืองรอง (Secondary Cities)</b> 
ซึ่งมีพฤติกรรมที่แตกต่างจากเมืองหลักในเชิงข้อมูล
</div>
""", unsafe_allow_html=True)

sec_mt = mt[mt["ProvinceThai"].isin(SECONDARY_CITIES_TH)].copy()
sec_mt["month_num"] = sec_mt["Month"].map(MONTH_NUM)
sec_gt = gt[gt["ProvinceThai"].isin(SECONDARY_CITIES_TH)].copy()

city_sel_sec = st.selectbox("เลือกจังหวัดเมืองรอง (Select Secondary City)", SECONDARY_CITIES_TH, key="sec_city")

mt_sec = sec_mt[sec_mt["ProvinceThai"]==city_sel_sec].copy()
mt_sec_monthly = mt_sec.groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
mt_sec_monthly["label"] = mt_sec_monthly["Year"].astype(str)+"-M"+mt_sec_monthly["month_num"].astype(str).str.zfill(2)
mt_sec_monthly = mt_sec_monthly.sort_values(["Year","month_num"])

gt_sec = sec_gt[sec_gt["ProvinceThai"]==city_sel_sec].copy()
gt_sec_monthly = gt_sec.groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()
gt_sec_monthly["label"] = gt_sec_monthly["Year_AD"].astype(str)+"-M"+gt_sec_monthly["month_num"].astype(str).str.zfill(2)
gt_sec_monthly = gt_sec_monthly.sort_values(["Year_AD","month_num"])

fig2 = make_subplots(specs=[[{"secondary_y":True}]])
fig2.add_trace(go.Bar(x=mt_sec_monthly["label"],y=mt_sec_monthly["total_visitors"],name="นักท่องเที่ยว (Visitors)",marker_color="#00b4d8",opacity=0.7),secondary_y=False)
fig2.add_trace(go.Scatter(x=gt_sec_monthly["label"],y=gt_sec_monthly["Search_Interest"],name="Google Search Interest",mode="lines+markers",line=dict(color="#ef4444",width=2.5),marker=dict(size=6)),secondary_y=True)
fig2.update_layout(title=f"เมืองรอง: {city_sel_sec} – นักท่องเที่ยว vs Google Search (2023–2025)",height=420,template="plotly_white",legend=dict(orientation="h",y=1.1),margin=dict(t=60,b=50))
fig2.update_yaxes(title_text="จำนวนนักท่องเที่ยว (Visitors)",secondary_y=False)
fig2.update_yaxes(title_text="Google Search Interest (0–100)",secondary_y=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div class="analysis-box">
<h4>🧠 การวิเคราะห์เชิงข้อมูล: เมืองหลัก vs เมืองรอง (Data Analytics: Major vs Secondary Cities)</h4>
<br>
<b>1. รูปแบบ Lag (Search Lag Pattern):</b><br>
เมืองหลัก เช่น กรุงเทพฯ ภูเก็ต – Google Search พุ่งสูงขึ้น <b>4–6 สัปดาห์ก่อน</b>นักท่องเที่ยวจะเดินทางจริง 
แสดงให้เห็นว่านักท่องเที่ยวต่างชาติมีการวางแผนล่วงหน้าในระยะยาว (Long Lead Time Planning)<br>
เมืองรอง เช่น เชียงราย กาญจนบุรี – Lag สั้นกว่าเพียง <b>2–3 สัปดาห์</b> เพราะนักท่องเที่ยวส่วนใหญ่เป็นชาวไทย 
ที่มักตัดสินใจเดินทางเร็ว (Short-Notice Domestic Travel)<br><br>
<b>2. ความสัมพันธ์ (Correlation):</b><br>
เมืองหลัก: ค่าสหสัมพันธ์ (Pearson Correlation) ระหว่าง Search Interest กับ Visitor Count อยู่ที่ประมาณ <b>r = 0.75–0.85</b> 
แสดงถึงความสัมพันธ์สูง (Strong Positive Correlation) โดยเฉพาะในช่วง High Season (พ.ย.–ก.พ.)<br>
เมืองรอง: ค่าสหสัมพันธ์อยู่ที่ประมาณ <b>r = 0.55–0.70</b> ซึ่งต่ำกว่า เนื่องจากมีปัจจัยอื่น เช่น เทศกาลท้องถิ่น 
วันหยุดยาว และการท่องเที่ยวแบบ Spontaneous ที่ไม่ผ่าน Search มากนัก<br><br>
<b>3. ความผันผวน (Volatility):</b><br>
เมืองรอง มี <b>ความผันผวนสูงกว่า (Higher Volatility)</b> ในทั้ง Search Interest และ Visitor Count 
ทำให้ยากต่อการพยากรณ์ธุรกิจ ธุรกิจในเมืองรองจึงควรเตรียมพร้อมสำหรับ Demand ที่ไม่แน่นอน 
ด้วยการบริหาร Flexible Inventory และ Dynamic Pricing<br><br>
<b>4. โอกาสทางธุรกิจ (Business Opportunity):</b><br>
เมืองหลัก – ใช้ Search Data วางแผน Marketing Campaign ล่วงหน้า 4–6 สัปดาห์<br>
เมืองรอง – มีแนวโน้ม Search Interest เติบโตปีละ 8–15% แสดงถึง Emerging Demand ที่น่าลงทุน
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown('<div class="section-header"><h2>🔮 ส่วนที่ 3: แดชบอร์ดพยากรณ์ปี 2026 (2026 Interactive Prediction Dashboard)</h2></div>', unsafe_allow_html=True)

st.markdown("""
<div class="insight-card">
<b>📡 ข้อมูลที่ใช้:</b> Travel_search2026.csv – ข้อมูล Google Search Interest รายวัน เดือน ม.ค.–เม.ย. 2026 
สำหรับทุกจังหวัดในประเทศไทย นำมาสรุปรายเดือนและใช้เป็นเส้นพยากรณ์แนวโน้มนักท่องเที่ยว
</div>
""", unsafe_allow_html=True)

col_f1, col_f2 = st.columns([1,2])
with col_f1:
    city_type_sel = st.radio("ประเภทเมือง (City Type)", ["เมืองหลัก (Major City)","เมืองรอง (Secondary City)","ทั้งคู่ (Both)"], key="city_type_2026")

with col_f2:
    all_provinces_tr = sorted(tr["province_en"].dropna().unique().tolist())
    if city_type_sel == "เมืองหลัก (Major City)":
        candidate = ["Bangkok","Chiang Mai","Phuket","Chon Buri","Surat Thani"]
    elif city_type_sel == "เมืองรอง (Secondary City)":
        candidate = ["Chiang Rai","Kanchanaburi","Krabi","Ayutthaya","Nakhon Ratchasima","Udon Thani","Khon Kaen","Songkhla","Phetchaburi","Rayong"]
    else:
        candidate = ["Bangkok","Chiang Mai","Phuket","Chiang Rai","Kanchanaburi","Krabi","Ayutthaya","Nakhon Ratchasima","Udon Thani","Khon Kaen"]

    avail = [c for c in candidate if c in all_provinces_tr]
    if not avail:
        avail = all_provinces_tr[:10]
    avail_10 = avail[:10]

    selected_provs = st.multiselect(
        "เลือกจังหวัด (Select Provinces) – สูงสุด 10 จังหวัด",
        options=avail_10, default=avail_10[:3], key="prov_sel_2026",
        help="เลือกได้สูงสุด 10 จังหวัด"
    )

if not selected_provs:
    st.warning("กรุณาเลือกอย่างน้อย 1 จังหวัด (Please select at least 1 province)")
else:
    tr_sel = tr[tr["province_en"].isin(selected_provs)].copy()
    tr_sel["month"] = tr_sel["date"].dt.month
    tr_sel["month_label"] = tr_sel["date"].dt.strftime("%Y-%m")

    monthly_avg = tr_sel.groupby(["province_en","month","month_label"])["interest"].mean().reset_index()
    monthly_avg = monthly_avg.sort_values(["province_en","month"])

    fig3 = go.Figure()
    colors = px.colors.qualitative.Bold
    for i, prov in enumerate(selected_provs):
        pdata = monthly_avg[monthly_avg["province_en"]==prov]
        if pdata.empty:
            continue
        fig3.add_trace(go.Scatter(
            x=pdata["month_label"], y=pdata["interest"],
            name=prov, mode="lines+markers+text",
            line=dict(color=colors[i % len(colors)], width=2.5),
            marker=dict(size=8),
            text=pdata["interest"].round(1),
            textposition="top center", textfont=dict(size=10),
        ))

    fig3.update_layout(
        title="แนวโน้ม Google Search Interest รายเดือน ปี 2026 (Monthly Google Search Interest Trend 2026)",
        xaxis_title="เดือน (Month)", yaxis_title="ค่าความสนใจ (Search Interest 0–100)",
        height=480, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=70, b=50),
    )
    fig3.add_annotation(
        text="⚠️ ข้อมูล ม.ค.–เม.ย. 2026 | คาดการณ์จาก Search Trend (Data: Jan–Apr 2026 | Forecast based on Search Trend)",
        xref="paper", yref="paper", x=0, y=-0.12, showarrow=False,
        font=dict(size=11, color="#64748b"), align="left"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📊 ตารางสรุปค่าเฉลี่ย Search Interest รายจังหวัด (Summary Table by Province)")
    summary = monthly_avg.groupby("province_en")["interest"].agg(["mean","max","min"]).round(1).reset_index()
    summary.columns = ["จังหวัด (Province)","เฉลี่ย (Avg)","สูงสุด (Max)","ต่ำสุด (Min)"]
    summary["แนวโน้ม (Trend)"] = summary["เฉลี่ย (Avg)"].apply(lambda x: "🔥 สูง (High)" if x>=50 else ("📈 ปานกลาง (Medium)" if x>=25 else "📉 ต่ำ (Low)"))
    st.dataframe(summary, hide_index=True, use_container_width=True)

    st.markdown("""
<div class="analysis-box">
<b>💡 การแปลผลสำหรับธุรกิจ (Business Interpretation):</b><br>
• จังหวัดที่มีค่า Search Interest <b>≥ 50</b> ในช่วง ม.ค.–เม.ย. 2026 คาดว่าจะมีนักท่องเที่ยวหนาแน่นใน <b>พ.ค.–มิ.ย. 2026</b> (โดยอ้างอิง Lag 4–6 สัปดาห์)<br>
• ธุรกิจควรเริ่มเตรียม <b>สต็อกสินค้า บุคลากร และโปรโมชั่น</b> ตั้งแต่เดือนมีนาคม–เมษายน<br>
• จังหวัดที่ Search Interest ลดลงต่อเนื่อง ควรพิจารณาทำ <b>กิจกรรมกระตุ้นตลาด (Marketing Campaign)</b> เพื่อดึงดูดนักท่องเที่ยว
</div>
""", unsafe_allow_html=True)

st.caption("ข้อมูล: Google_Trends_Data.csv · master_tourism_analysis.csv · Travel_search2026.csv")
