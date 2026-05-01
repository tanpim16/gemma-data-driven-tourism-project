import streamlit as st

st.set_page_config(
    page_title="Introduction | Gemma City-Smart Strategist",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Prompt:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
        .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
        h2 { margin-bottom: 0px !important; }
        p { margin-bottom: 5px !important; }
        hr { margin-top: 10px !important; margin-bottom: 15px !important; }
        .stat-card {
            border-radius: 16px;
            padding: 1.2rem 1rem;
            text-align: center;
            color: white;
        }
        .stat-number { font-size: 2.2rem; font-weight: 800; margin: 0 0 2px 0; line-height: 1.1; }
        .stat-label { font-size: 0.85rem; opacity: 0.9; margin: 0; }
        .persona-card {
            background: white;
            border-radius: 16px;
            padding: 1.3rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            border-top: 5px solid #1E3D59;
            height: 100%;
        }
        .persona-card.entrepreneur { border-top-color: #FF6E40; }
        .persona-card.government { border-top-color: #27ae60; }
        .step-box {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 0.9rem;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='text-align:center;color:#1E3D59;margin-bottom:4px;'>🧠 Gemma City-Smart Strategist</h2>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:#576574;font-size:16px;'>"
    "ยกระดับการท่องเที่ยว 77 จังหวัด · กระตุ้น 55 เมืองรอง ด้วยพลัง <b>Gemma 4</b></p>",
    unsafe_allow_html=True
)

st.divider()

# ── Stats Cards ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
stats = [
    ("#1E3D59", "#2d6a9f", "77", "จังหวัดทั่วประเทศไทย"),
    ("#FF6E40", "#ff9370", "55", "เมืองรองที่รอการค้นพบ"),
    ("#27ae60", "#2ecc71", "3", "ปีข้อมูลสถิติ (2566–2568)"),
    ("#8e44ad", "#9b59b6", "39", "เทศกาลสำคัญทั่วประเทศ"),
]
for col, (c_start, c_end, num, label) in zip([c1, c2, c3, c4], stats):
    with col:
        st.markdown(
            f'<div class="stat-card" style="background:linear-gradient(135deg,{c_start} 0%,{c_end} 100%);">'
            f'<p class="stat-number">{num}</p>'
            f'<p class="stat-label">{label}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────────────────────────
col_left, spacer, col_right = st.columns([1, 0.05, 1.5])

with col_left:
    st.markdown("#### 🎯 วัตถุประสงค์หลัก")
    st.write(
        "ลดความเหลื่อมล้ำทางเศรษฐกิจระหว่าง **เมืองหลัก** และ **เมืองรอง** "
        "โดยเปลี่ยนข้อมูลดิบให้กลายเป็น Actionable Insights "
        "ผ่านพลังของ **Gemma 4**"
    )
    st.markdown("#### 💡 ทำไมต้องเมืองรอง?")
    st.info(
        "เมืองรอง 55 จังหวัด มีรายได้เฉลี่ยน้อยกว่าเมืองหลักถึง **4–6 เท่า** "
        "แต่ยังมีศักยภาพด้านวัฒนธรรม ธรรมชาติ และอาหารที่ไม่แพ้กัน "
        "เพียงแค่ยังขาดการ **นำเสนอเรื่องราวที่ใช่**"
    )

with col_right:
    try:
        st.image("picture/PIC_Amazing TH.jpg", use_container_width=True)
        st.markdown(
            "<p style='text-align:right;color:#95a5a6;font-size:11px;margin-top:-10px;'>"
            "ขอขอบพระคุณรูปภาพจาก การท่องเที่ยวแห่งประเทศไทย</p>",
            unsafe_allow_html=True
        )
    except Exception:
        pass

st.divider()

# ── Persona Cards ─────────────────────────────────────────────────────────────
st.markdown("#### 🧩 แพลตฟอร์มนี้ออกแบบมาสำหรับทุกกลุ่ม")
st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
personas = [
    ("persona-card", "✈️ นักท่องเที่ยว",
     "วางแผนทริปแบบ 3 วัน 2 คืน พร้อมแนะนำ **เมืองรองใกล้เคียง** ที่ไม่ควรพลาด พร้อมแผนที่และพยากรณ์อากาศ",
     "🗺️ Trip Planner AI"),
    ("persona-card entrepreneur", "🏪 ผู้ประกอบการ",
     "รับ **กลยุทธ์การตลาด** และไอเดียโปรโมชั่นที่สอดคล้องกับเทศกาลและข้อมูลตลาดจริงของจังหวัดคุณ",
     "🗺️ Trip Planner AI"),
    ("persona-card government", "🏛️ ภาครัฐ",
     "วิเคราะห์ **ช่องว่างรายได้** High-Low Season และรับข้อเสนอนโยบาย Event เพื่อกระตุ้นเศรษฐกิจ",
     "🗺️ Trip Planner AI"),
]
for col, (css_class, title, desc, link) in zip([p1, p2, p3], personas):
    with col:
        st.markdown(
            f'<div class="{css_class}">'
            f'<h4 style="margin-bottom:0.5rem">{title}</h4>'
            f'<p style="color:#576574;font-size:0.9rem">{desc}</p>'
            f'<p style="margin-top:0.8rem;font-weight:600;color:#1E3D59">→ ไปที่หน้า {link}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

st.divider()

# ── How-to Steps ──────────────────────────────────────────────────────────────
s1, s2, s3 = st.columns(3)
steps = [
    ("🔍", "ขั้นที่ 1: ส่องข้อมูล", "ดูเทรนด์และช่องว่างที่หน้า Market Analysis"),
    ("📅", "ขั้นที่ 2: เช็กเทศกาล", "ดูปฏิทินเทศกาลที่หน้า Tourism Database"),
    ("🤖", "ขั้นที่ 3: ปรึกษา AI", "ให้ Gemma 4 ช่วยวางแผนที่หน้า Trip Planner"),
]
for col, (icon, title, desc) in zip([s1, s2, s3], steps):
    with col:
        st.markdown(
            f'<div class="step-box">'
            f'<p style="font-size:1.8rem;margin-bottom:0.2rem">{icon}</p>'
            f'<p style="font-weight:700;margin-bottom:0.2rem">{title}</p>'
            f'<p style="color:#576574;font-size:0.88rem">{desc}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

st.divider()
st.caption(
    "Gemma City-Smart Strategist · Powered by Gemma 4 (gemma-4-31b-it) · "
    "ข้อมูล: กระทรวงการท่องเที่ยวและกีฬา ปี 2566–2568"
)
