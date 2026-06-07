import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import re
import google.generativeai as genai

# --- การตั้งค่าหน้ากระดาษ ---
st.set_page_config(page_title="แผนธุรกิจการท่องเที่ยวไทย (Thailand Tourism Business Planning)", page_icon="📊", layout="wide")

# --- CSS Styling (ปรับลดขนาด Font Header และปรับแต่งส่วนหัวข้อ) ---
st.markdown("""
<style>
.section-header { 
    background: linear-gradient(135deg,#0077B6,#00b4d8); 
    color:white; 
    padding:0.8rem 1.2rem; 
    border-radius:10px; 
    margin:1rem 0; 
}
.section-header h4 { 
    margin: 0; 
    font-size: 1.5rem; 
    font-weight: 600;
}
.insight-card { background:#f0f9ff; border-left:4px solid #0077B6; border-radius:8px; padding:1rem 1.5rem; margin:0.8rem 0; }
.analysis-box { background:#fff7ed; border-left:4px solid #f97316; border-radius:8px; padding:1rem 1.5rem; margin:0.8rem 0; }
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MONTH_NUM = {m:i+1 for i,m in enumerate(MONTH_ORDER)}
MONTH_TH_MAP = {1:"ม.ค.", 2:"ก.พ.", 3:"มี.ค.", 4:"เม.ย.", 5:"พ.ค.", 6:"มิ.ย.", 7:"ก.ค.", 8:"ส.ค.", 9:"ก.ย.", 10:"ต.ค.", 11:"พ.ย.", 12:"ธ.ค."}

# สร้างแกน x เรียงตามเวลาสำหรับกราฟ 1 และ 2
GLOBAL_TIME_LABELS = []
for y in [2023, 2024, 2025]:
    y_str = str(y)[-2:] 
    for m in range(1, 13):
        GLOBAL_TIME_LABELS.append(f"{MONTH_TH_MAP[m]} {y_str}")

@st.cache_data
def load_data():
    gt = pd.read_csv(os.path.join(DATA,"Google_Trends_Data.csv"))
    mt = pd.read_csv(os.path.join(DATA,"master_tourism_analysis.csv"))
    tr_path = os.path.join(DATA,"Travel_search2026.csv")
    if not os.path.exists(tr_path): tr_path = os.path.join(DATA,"Frommongodb2026.csv")
    tr = pd.read_csv(tr_path)
    
    tr["date"] = pd.to_datetime(tr["date"])
    tr["interest"] = pd.to_numeric(tr["interest"], errors="coerce").fillna(0)
    mt["total_visitors"] = pd.to_numeric(mt["total_visitors"], errors="coerce").fillna(0)
    gt["Search_Interest"] = pd.to_numeric(gt["Search_Interest"], errors="coerce").fillna(0)
    
    if "Year" in mt.columns:
        mt["Year"] = pd.to_numeric(mt["Year"], errors="coerce")
        mt["Year"] = mt["Year"].apply(lambda x: x - 543 if pd.notnull(x) and x > 2500 else x)
    if "Year_AD" in gt.columns:
        gt["Year_AD"] = pd.to_numeric(gt["Year_AD"], errors="coerce")
        gt["Year_AD"] = gt["Year_AD"].apply(lambda x: x - 543 if pd.notnull(x) and x > 2500 else x)
        
    gt["month_num"] = gt["Month"].map(MONTH_NUM)
    mt["month_num"] = mt["Month"].map(MONTH_NUM)
    
    prov_info = mt[['ProvinceThai', 'ProvinceEN', 'City_type_TH']].drop_duplicates().dropna()
    majors = sorted(prov_info[prov_info['City_type_TH'] == 'เมืองหลัก']['ProvinceThai'].unique().tolist())
    secs = sorted(prov_info[prov_info['City_type_TH'] == 'เมืองรอง']['ProvinceThai'].unique().tolist())
    en_to_th = dict(zip(prov_info['ProvinceEN'], prov_info['ProvinceThai']))
    
    return gt, mt, tr, majors, secs, en_to_th

gt, mt, tr, MAJOR_CITIES_TH, SECONDARY_CITIES_TH, EN_TO_TH_MAP = load_data()

st.title("📊 แผนธุรกิจการท่องเที่ยวไทย (Thailand Tourism Business Planning)")
st.markdown("วิเคราะห์ข้อมูลเชิงลึกเพื่อวางแผนธุรกิจ โดยใช้ข้อมูล Google Trends และสถิตินักท่องเที่ยว ปี 2023–2026")

# ----------------------------------------------------------------
# เมืองหลัก – นักท่องเที่ยว vs Google Search (2023–2025)
# ----------------------------------------------------------------
st.divider()
st.markdown('<div class="section-header"><h4>📈 เมืองหลัก – นักท่องเที่ยว vs Google Search (2023–2025)</h4></div>', unsafe_allow_html=True)

major_options = ["ทั่วประเทศ", "รวมเมืองหลัก"] + MAJOR_CITIES_TH
city_sel_major = st.multiselect("เลือกตัวเลือกหรือจังหวัด (เมืองหลัก)", major_options, default=["รวมเมืองหลัก"], max_selections=10, key="major_city")

if city_sel_major:
    fig1 = make_subplots(specs=[[{"secondary_y":True}]])
    for idx, sel in enumerate(city_sel_major):
        if sel == "ทั่วประเทศ":
            df_mt = mt.groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
            df_gt = gt.groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()
        elif sel == "รวมเมืองหลัก":
            df_mt = mt[mt["ProvinceThai"].isin(MAJOR_CITIES_TH)].groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
            df_gt = gt[gt["ProvinceThai"].isin(MAJOR_CITIES_TH)].groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()
        else:
            df_mt = mt[mt["ProvinceThai"]==sel].groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
            df_gt = gt[gt["ProvinceThai"]==sel].groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()

        df_mt["label"] = df_mt["month_num"].map(MONTH_TH_MAP) + " " + df_mt["Year"].astype(int).astype(str).str[-2:]
        df_gt["label"] = df_gt["month_num"].map(MONTH_TH_MAP) + " " + df_gt["Year_AD"].astype(int).astype(str).str[-2:]
        fig1.add_trace(go.Scatter(x=df_mt["label"], y=df_mt["total_visitors"], name=f"นทท. ({sel})", mode="lines+markers"), secondary_y=False)
        fig1.add_trace(go.Scatter(x=df_gt["label"], y=df_gt["Search_Interest"], name=f"Search ({sel})", mode="lines", line=dict(dash="dash")), secondary_y=True)

    fig1.update_layout(height=450, template="plotly_white", legend=dict(orientation="h", y=-0.2), xaxis=dict(categoryorder="array", categoryarray=GLOBAL_TIME_LABELS))
    fig1.update_yaxes(title_text="จำนวนนักท่องเที่ยว (คน)", secondary_y=False)
    fig1.update_yaxes(title_text="Search Interest (0-30)", secondary_y=True, range=[0, 30], showgrid=False)
    st.plotly_chart(fig1, use_container_width=True)

# ----------------------------------------------------------------
# เมืองรอง – นักท่องเที่ยว vs Google Search (2023–2025)
# ----------------------------------------------------------------
st.divider()
st.markdown('<div class="section-header"><h4>🏘️ เมืองรอง – นักท่องเที่ยว vs Google Search (2023–2025)</h4></div>', unsafe_allow_html=True)
sec_options = ["ทั่วประเทศ", "รวมเมืองรอง"] + SECONDARY_CITIES_TH
city_sel_sec = st.multiselect("เลือกตัวเลือกหรือจังหวัด (เมืองรอง)", sec_options, default=["รวมเมืองรอง"], max_selections=10, key="sec_city")

if city_sel_sec:
    fig2 = make_subplots(specs=[[{"secondary_y":True}]])
    for idx, sel in enumerate(city_sel_sec):
        if sel == "ทั่วประเทศ":
            df_mt = mt.groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
            df_gt = gt.groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()
        elif sel == "รวมเมืองรอง":
            df_mt = mt[mt["ProvinceThai"].isin(SECONDARY_CITIES_TH)].groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
            df_gt = gt[gt["ProvinceThai"].isin(SECONDARY_CITIES_TH)].groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()
        else:
            df_mt = mt[mt["ProvinceThai"]==sel].groupby(["Year","month_num"])["total_visitors"].sum().reset_index()
            df_gt = gt[gt["ProvinceThai"]==sel].groupby(["Year_AD","month_num"])["Search_Interest"].mean().reset_index()

        df_mt["label"] = df_mt["month_num"].map(MONTH_TH_MAP) + " " + df_mt["Year"].astype(int).astype(str).str[-2:]
        df_gt["label"] = df_gt["month_num"].map(MONTH_TH_MAP) + " " + df_gt["Year_AD"].astype(int).astype(str).str[-2:]
        fig2.add_trace(go.Scatter(x=df_mt["label"], y=df_mt["total_visitors"], name=f"นทท. ({sel})", mode="lines+markers"), secondary_y=False)
        fig2.add_trace(go.Scatter(x=df_gt["label"], y=df_gt["Search_Interest"], name=f"Search ({sel})", mode="lines", line=dict(dash="dash")), secondary_y=True)

    fig2.update_layout(height=450, template="plotly_white", legend=dict(orientation="h", y=-0.2), xaxis=dict(categoryorder="array", categoryarray=GLOBAL_TIME_LABELS))
    fig2.update_yaxes(title_text="จำนวนนักท่องเที่ยว (คน)", secondary_y=False)
    fig2.update_yaxes(title_text="Search Interest (0-30)", secondary_y=True, range=[0, 30], showgrid=False)
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------------------
# กราฟ 3 แดชบอร์ดพยากรณ์ปี 2026 (ระบบดั้งเดิม)
# ----------------------------------------------------------------
st.divider()
st.markdown('<div class="section-header"><h4>🔮 แดชบอร์ดพยากรณ์ปี 2026 (รวมปี 2025)</h4></div>', unsafe_allow_html=True)

col_f1, col_f2 = st.columns([1,2])
with col_f1:
    city_type_sel = st.selectbox("ประเภทเมือง", ["ทั่วประเทศ", "เมืองหลัก (Major City)", "เมืองรอง (Secondary City)"], key="city_type_2026")

with col_f2:
    if city_type_sel == "เมืองหลัก (Major City)": options = ["รวมเมืองหลัก"] + MAJOR_CITIES_TH
    elif city_type_sel == "เมืองรอง (Secondary City)": options = ["รวมเมืองรอง"] + SECONDARY_CITIES_TH
    else: options = ["รวมทั่วประเทศ"] + sorted(list(set(MAJOR_CITIES_TH + SECONDARY_CITIES_TH)))
    selected_prov = st.selectbox("เลือกตัวเลือกหรือจังหวัด", options=options, key="prov_sel_2026")

if selected_prov:
    th_name_list = MAJOR_CITIES_TH if selected_prov == "รวมเมืองหลัก" else (SECONDARY_CITIES_TH if selected_prov == "รวมเมืองรอง" else (sorted(list(set(MAJOR_CITIES_TH + SECONDARY_CITIES_TH))) if selected_prov == "รวมทั่วประเทศ" else [selected_prov]))
    
    prov_metrics = []
    for th_name in th_name_list:
        v_sum = mt[mt["ProvinceThai"]==th_name]["total_visitors"].sum()
        s_sum = gt[gt["ProvinceThai"]==th_name]["Search_Interest"].sum()
        ratio = v_sum / s_sum if s_sum > 0 else 3000
        prov_metrics.append({"prov_th_std": th_name, "ratio": ratio, "lag": 1 if th_name in MAJOR_CITIES_TH else 2})
    df_metrics = pd.DataFrame(prov_metrics)

    tr_temp = tr.copy()
    tr_temp["prov_th_std"] = tr_temp["province_en"].map(EN_TO_TH_MAP).fillna(tr_temp["province_th"])
    tr_sel = tr_temp[tr_temp["prov_th_std"].isin(th_name_list)].copy()
    prov_search_2026 = tr_sel.groupby(["prov_th_std", tr_sel["date"].dt.month])["interest"].mean().reset_index().rename(columns={"date":"month"})
    prov_search_2026["year"] = 2026

    gt_2025 = gt[(gt["ProvinceThai"].isin(th_name_list)) & (gt["Year_AD"] == 2025) & (gt["month_num"].isin([11, 12]))]
    gt_2025_search = gt_2025.groupby(["ProvinceThai", "month_num"])["Search_Interest"].mean().reset_index().rename(columns={"ProvinceThai": "prov_th_std", "month_num": "month", "Search_Interest": "interest"})
    gt_2025_search["year"] = 2025

    all_search = pd.concat([gt_2025_search, prov_search_2026], ignore_index=True).merge(df_metrics, on="prov_th_std", how="left")
    all_search["abs_m"] = all_search["year"] * 12 + all_search["month"] - 1
    all_search["p_abs_m"] = all_search["abs_m"] + all_search["lag"]
    all_search["p_year"], all_search["p_month"] = all_search["p_abs_m"] // 12, all_search["p_abs_m"] % 12 + 1
    all_search["p_vis"] = all_search["interest"] * all_search["ratio"]

    pred_2026_agg = all_search[all_search["p_year"] == 2026].groupby("p_month")["p_vis"].sum().reset_index()
    search_agg = prov_search_2026.groupby("month")["interest"].mean().reset_index()
    mt_2025_agg = mt[(mt["Year"] == 2025) & (mt["ProvinceThai"].isin(th_name_list))].groupby("month_num")["total_visitors"].sum().reset_index()

    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(go.Scatter(x=search_agg["month"].map(MONTH_TH_MAP), y=search_agg["interest"], name="Search Interest 2026", line=dict(color="#f97316")), secondary_y=True)
    if not mt_2025_agg.empty: fig3.add_trace(go.Scatter(x=mt_2025_agg["month_num"].map(MONTH_TH_MAP), y=mt_2025_agg["total_visitors"], name="นทท. 2025", line=dict(color="#10b981", dash="dash")), secondary_y=False)
    fig3.add_trace(go.Scatter(x=pred_2026_agg["p_month"].map(MONTH_TH_MAP), y=pred_2026_agg["p_vis"], name="พยากรณ์ นทท. 2026 (ดั้งเดิม)", line=dict(color="#0077B6", dash="dot"), marker=dict(symbol="diamond")), secondary_y=False)

    fig3.update_layout(title=f"กราฟที่ 3: พยากรณ์ดั้งเดิม สำหรับ {selected_prov}", height=500, template="plotly_white", legend=dict(orientation="h", y=-0.3), xaxis=dict(categoryorder="array", categoryarray=list(MONTH_TH_MAP.values())))
    fig3.update_yaxes(title_text="จำนวนนักท่องเที่ยว (คน)", secondary_y=False)
    fig3.update_yaxes(title_text="Search Interest (0-30)", secondary_y=True, range=[0, 30], showgrid=False)
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------------------
    # กราฟ 4: ผลการพยากรณ์จำนวนนักท่องเที่ยวโดย Gemini AI Agent
    # ----------------------------------------------------------------
    st.divider()
    st.markdown('<div class="section-header"><h4>🤖 ผลการพยากรณ์จำนวนนักท่องเที่ยวโดย Gemini AI Agent</h4></div>', unsafe_allow_html=True)

    # 1. การเลือกพื้นที่เป้าหมาย (ใช้ Column เหมือนเดิม)
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        gemini_city_type = st.selectbox("ประเภทเมือง (AI)", ["ทั้งหมด", "เมืองหลัก", "เมืองรอง"], key="gemini_type")

    with col_g2:
        if gemini_city_type == "เมืองหลัก": gemini_options = MAJOR_CITIES_TH
        elif gemini_city_type == "เมืองรอง": gemini_options = SECONDARY_CITIES_TH
        else: gemini_options = sorted(list(set(MAJOR_CITIES_TH + SECONDARY_CITIES_TH)))
        
        gemini_selected_provs = st.multiselect("เลือกจังหวัดเป้าหมาย (สูงสุด 5 จังหวัด)", options=gemini_options, default=gemini_options[:1], max_selections=5, key="gemini_provs")

    # ---------------------------------------------------------
    # 💡 2. วาง API KEY ของคุณตรงนี้ (ลบข้อความภาษาไทยออกแล้วใส่ Key จริง)
    # ---------------------------------------------------------
    try:
        gemini_key = st.secrets["gemini"]["TANYA_GEMINI_API_KEY"]
    except (KeyError, AttributeError):
        gemini_key = "" # ถ้าไม่เจอ Key ให้เป็นค่าว่าง
    
    # เช็คว่าผู้ใช้เปลี่ยน Key หรือยัง
    if not gemini_key:
        st.error(
            "⚠️ ไม่พบ Gemini API Key. กรุณาเพิ่มลงในไฟล์ "
            "[.streamlit/secrets.toml](/?file=/workspaces/gemma-data-driven-tourism-project/.streamlit/secrets.toml) ของคุณภายใต้ `[gemini]`"
        )
    else:
        st.success(f"✅ พร้อมใช้งาน AI (ตรวจพบ Key ที่ลงท้ายด้วย ...{gemini_key[-4:]})")

    # 3. การทำงานเมื่อกดปุ่ม
    if st.button("🚀 รัน AI Agent (Gemini) เพื่อพยากรณ์ใหม่", type="primary"):
        if not gemini_key:
            st.error("❌ ไม่สามารถประมวลผลได้ กรุณาใส่ API Key ให้เรียบร้อยก่อน")
        elif not gemini_selected_provs:
            st.warning("⚠️ กรุณาเลือกอย่างน้อย 1 จังหวัด")
        else:
            with st.spinner("🧠 Gemini Agent กำลังวิเคราะห์แนวโน้มแต่ละจังหวัด..."):
                try:
                    # เชื่อมต่อกับระบบ Gemini
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash", # <--- อัปเดตเป็น Gemini 2.5 Flash
                        system_instruction="You are an expert Data Scientist. Analyze seasonal patterns. Return ONLY a JSON object where keys are province names and values are lists of 12 integers for 2026."
                    )

                    # เตรียมข้อมูลของทุกจังหวัดที่เลือกไว้
                    all_hist_str = ""
                    for p_name in gemini_selected_provs:
                        hist_df = mt[mt["ProvinceThai"] == p_name].groupby(["Year", "month_num"])["total_visitors"].sum().reset_index()
                        all_hist_str += f"--- Province: {p_name} ---\n"
                        for y in [2023, 2024, 2025]:
                            y_data = hist_df[hist_df["Year"] == y].sort_values("month_num")
                            if not y_data.empty:
                                month_data = [f"M{int(r['month_num'])}={int(r['total_visitors'])}" for _, r in y_data.iterrows()]
                                all_hist_str += f"Year {y}: " + ", ".join(month_data) + "\n"
                    
                    # สั่งให้ AI พยากรณ์
                    prompt = f"Data for multiple provinces:\n{all_hist_str}\nPredict Jan-Dec 2026 for each province. Return ONLY a valid JSON object like: {{'ProvinceName': [12 values], ...}}"
                    response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.2))
                    
                    # สกัดข้อมูล JSON ที่ AI ตอบกลับมา
                    import json
                    out_text = response.text
                    match = re.search(r'\{.*\}', out_text.replace('\n', ''), re.DOTALL)
                    
                    if match:
                        gemini_results = json.loads(match.group(0).replace("'", '"'))
                        st.session_state['gemini_multi_results'] = gemini_results
                        st.success("✅ Gemini Agent พยากรณ์สำเร็จสำหรับทุกจังหวัดที่เลือก!")
                    else:
                        st.error(f"⚠️ รูปแบบคำตอบจาก AI ไม่ถูกต้อง: {out_text}")
                except Exception as e:
                    st.error(f"❌ ระบบขัดข้อง: {e}")

    # 4. นำข้อมูลมาพล็อตลงกราฟ (ถ้ามีการคำนวณสำเร็จแล้ว)
    if 'gemini_multi_results' in st.session_state:
        results = st.session_state['gemini_multi_results']
        fig4 = go.Figure()
        
        # วนลูปวาดกราฟเส้นตามจำนวนจังหวัดที่เลือก
        for p_name, g_preds in results.items():
            if p_name in gemini_selected_provs: # กรองแสดงเฉพาะที่เลือกปัจจุบัน
                fig4.add_trace(go.Scatter(
                    x=list(MONTH_TH_MAP.values()), 
                    y=g_preds, 
                    name=f"🤖 {p_name} (Gemini)", 
                    mode="lines+markers"
                ))
                
        fig4.update_layout(
            title=f"กราฟที่ 4: ผลการพยากรณ์ Gemini สำหรับจังหวัดที่เลือก", 
            height=550, 
            template="plotly_white", 
            legend=dict(orientation="h", y=-0.2), 
            yaxis_title="จำนวนนักท่องเที่ยว (คน)"
        )
        st.plotly_chart(fig4, use_container_width=True)

st.caption("ข้อมูล: Google_Trends_Data.csv · master_tourism_analysis.csv · Travel_search2026.csv")