import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import time

# ─── 🏗️ Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CitySmart | AI Trip Planner",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 🎨 CSS (เน้นแก้กรอบว่างและจัดระเบียบตัวหนังสือ) ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1a1a2e; }
.stApp { background: #f5f3ef; }

/* ── Hero ── */
.hero { padding: 2rem 0 1rem 0; }
.hero-title { font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800; color: #12111a; }
.hero-title span { color: #6c63b5; }

/* ── Form Card ── */
.form-card {
    background: white; border-radius: 24px; padding: 2.5rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.04); margin-bottom: 2rem;
}

/* ── Weather Banner (กรอบที่พิมบอกว่าว่าง) ── */
.weather-banner {
    background: linear-gradient(135deg, #6c63b5 0%, #4a4090 100%);
    color: white; border-radius: 18px; padding: 1.5rem 2rem;
    margin-bottom: 2rem; box-shadow: 0 8px 20px rgba(108,99,181,0.2);
}
.weather-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.1rem; margin-bottom: 8px; }

/* ── Result Cards ── */
.result-card { 
    background: white; border-radius: 24px; padding: 2rem; 
    box-shadow: 0 4px 30px rgba(0,0,0,0.03); height: 100%; border-top: 6px solid #6c63b5; 
}
.gem-card { border-top: 6px solid #ff9933; }

/* ── Typography Fix ── */
.result-card h3 { font-family: 'Syne', sans-serif; font-size: 1.8rem; margin-bottom: 1rem; }
.result-card p, .result-card li { line-height: 1.8; margin-bottom: 0.5rem; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ─── ⚙️ AI & Data ───────────────────────────────────────────────────────────
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemma-4-31b-it')

@st.cache_data
def load_data():
    df_t = pd.read_csv('data/master_tourism_analysis.csv')
    df_f = pd.read_excel('data/Thailand_Festival_Master.xlsx')
    return df_t.dropna(subset=['ProvinceEN', 'Region_EN']), df_f

def call_ai_strict(prompt):
    """ฟังก์ชันสั่ง AI แบบเด็ดขาด ห้ามเพ้อเจ้อ"""
    try:
        response = model.generate_content(prompt)
        text = response.text
        # กรองเอาเฉพาะเนื้อหาจริง ตัดพวกร่าง (Draft/Check) ออกถ้าหลุดมา
        if "Day 1" in text:
            text = text.split("Day 1")[-1]
            return "Day 1" + text
        return text
    except:
        return "AI ยุ่งอยู่ ลองกดใหม่อีกครั้งครับ"

try:
    df_tour, df_fest = load_data()

    if 'main_res' not in st.session_state: st.session_state.main_res = ""
    if 'gem_res' not in st.session_state: st.session_state.gem_res = ""
    if 'weather_res' not in st.session_state: st.session_state.weather_res = ""

    # ─── 🌐 Language Switch ───────────────────────────────────────────────────
    lang_col, _ = st.columns([1, 5])
    with lang_col:
        st.session_state.lang = st.segmented_control("Lang", ["TH", "EN", "CN"], default=st.session_state.get('lang', 'TH'), label_visibility="collapsed")

    ui = {
        'TH': {
            'title': "วางแผนทริป", 'accent': "แบบสมาร์ท", 'sub': "คัดกรองข้อมูลเทศกาลและอากาศเพื่อทริปที่สมบูรณ์แบบ",
            'btn': "เริ่มสร้างแผนท่องเที่ยว ✨", 'dest': "เลือกจังหวัด", 'days': "กี่วันกี่คืน?", 'style': "สไตล์การเที่ยว",
            'weather_head': "☁️ อัปเดตสภาพอากาศและคำแนะนำการเดินทาง",
            'styles': ["คาเฟ่และถ่ายรูป 📸", "ธรรมชาติและภูเขา ⛰️", "วัฒนธรรมและวัด 🛕", "ตะลอนกินสตรีทฟู้ด 🍜", "พักผ่อนชิลล์ๆ 🧖‍♀️", "สายบาร์และกลางคืน 🍸"]
        },
        'EN': {
            'title': "Trip Planner", 'accent': "Smartly", 'sub': "Real-time insights for your perfect Thailand journey.",
            'btn': "Generate Itinerary ✨", 'dest': "Select Province", 'days': "Duration?", 'style': "Travel Style",
            'weather_head': "☁️ Local Weather & Travel Tips",
            'styles': ["Cafe & Photo 📸", "Nature & Mountains ⛰️", "Culture & Temples 🛕", "Street Food 🍜", "Relaxing & Spa 🧖‍♀️", "Nightlife & Bars 🍸"]
        }
    }
    t = ui.get(st.session_state.lang, ui['EN'])

    # ─── 🏛️ Hero ──────────────────────────────────────────────────────────────
    st.markdown(f'<div class="hero"><h1 class="hero-title">{t["title"]} <span>{t["accent"]}</span></h1><p>{t["sub"]}</p></div>', unsafe_allow_html=True)

    # ─── 📝 Form Section ──────────────────────────────────────────────────────
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2], gap="large")
    with c1:
        province = st.selectbox(f"📍 {t['dest']}", options=sorted(df_tour['ProvinceEN'].unique()))
        t_date = st.date_input("📅 วันเดินทาง", datetime.now())
    with c2:
        days = st.slider(f"☀️ {t['days']}", 1, 5, 3)
    with c3:
        # แก้ไข Styles ให้เปลี่ยนตามภาษาที่เลือก
        selected_style = st.multiselect(f"🎨 {t['style']}", options=t['styles'], default=[t['styles'][0]])
    
    if st.button(t['btn']):
        city_info = df_tour[df_tour['ProvinceEN'] == province].iloc[0]
        month = t_date.strftime('%B')
        
        # ค้นหาเมืองรองใน Region เดียวกัน
        neighbors = df_tour[(df_tour['City_type_EN'] == 'Secondary City') & (df_tour['Region_EN'] == city_info['Region_EN'])]
        st.session_state.gem_city = neighbors.sample(1)['ProvinceEN'].values[0] if not neighbors.empty else "Lampang"

        with st.spinner("AI กำลังคิดแผนเที่ยวให้คุณ..."):
            # 1. Weather Info (อุดรูโบ๋) - สั่งสั้นๆ ให้จบใน 2 ประโยค
            lang_cmd = "ภาษาไทยเท่านั้น" if st.session_state.lang == 'TH' else "English only"
            w_prompt = f"อากาศและคำแนะนำการเตรียมตัวไป {province} เดือน {month} สรุปใน 2 ประโยค ({lang_cmd}). ห้ามเกริ่นนำ."
            st.session_state.weather_res = call_ai_strict(w_prompt)

            # 2. Main Itinerary
            lang_rule = f"ตอบเป็น {lang_cmd} เท่านั้น ห้ามผสมภาษาอื่น"
            p_main = f"""
            จงวางแผนเที่ยว {province} {days} วัน {days-1} คืน 
            สไตล์ {selected_style} ในเดือน {month}
            เงื่อนไขเด็ดขาด: {lang_rule}, ห้ามทวนคำสั่ง, ห้ามเขียนร่าง, เริ่มที่ Day 1 ทันที, แนะนำที่พัก 1 แห่ง
            Format: ใช้ **Day X** และ Bullet points
            """
            st.session_state.main_res = call_ai_strict(p_main)

            # 3. Gem Plan (ขนานกัน)
            if city_info['City_type_EN'] == 'Major City':
                time.sleep(1.2) # กัน Busy
                p_gem = f"วางแผนเที่ยว {st.session_state.gem_city} (เมืองรองใกล้ {province}) แบบเดียวกันเป๊ะ {lang_rule}. เริ่ม Day 1 ทันที."
                st.session_state.gem_res = call_ai_strict(p_gem)
            else:
                st.session_state.gem_res = ""

    st.markdown('</div>', unsafe_allow_html=True)

    # ─── 📊 ผลลัพธ์ (Display) ──────────────────────────────────────────────────
    # 1. Weather Banner (อุดรูโบ๋ด้วยข้อมูลอากาศจริงๆ)
    if st.session_state.weather_res:
        st.markdown(f"""
        <div class="weather-banner">
            <div class="weather-title">{t['weather_head']}</div>
            <div>{st.session_state.weather_res}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Travel Plans
    if st.session_state.main_res:
        if st.session_state.gem_res:
            col_l, col_r = st.columns(2, gap="large")
            with col_l:
                st.markdown(f'<div class="result-card"><div style="color:#6c63b5; font-weight:700; font-size:0.7rem; text-transform:uppercase; margin-bottom:5px;">Main Destination</div><h3>📍 {province}</h3>', unsafe_allow_html=True)
                st.markdown(st.session_state.main_res)
                st.markdown('</div>', unsafe_allow_html=True)
            with col_r:
                st.markdown(f'<div class="result-card gem-card"><div style="color:#ff9933; font-weight:700; font-size:0.7rem; text-transform:uppercase; margin-bottom:5px;">Hidden Gem Suggestion</div><h3>✦ {st.session_state.gem_city}</h3><p style="font-size:0.8rem; color:#8b7d6b;">🚗 เดินทางจาก {province} สะดวก (2-3 ชม.)</p>', unsafe_allow_html=True)
                st.markdown(st.session_state.gem_res)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="result-card"><h3>📍 {province}</h3>', unsafe_allow_html=True)
            st.markdown(st.session_state.main_res)
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")