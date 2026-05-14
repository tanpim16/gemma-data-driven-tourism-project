import streamlit as st

st.set_page_config(
    page_title="Gemma City-Smart Strategist",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Prompt', sans-serif !important;
}
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
}

/* ── Eyebrow tag ── */
.eyebrow {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #1e3d59;
    background: #e8f0f8;
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 1.1rem;
}

/* ── Hero left ── */
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #111827;
    line-height: 1.2;
    margin: 0 0 0.9rem 0;
}
.hero-title em { font-style: normal; color: #1e3d59; }
.hero-sub {
    font-size: 0.95rem;
    color: #6b7280;
    line-height: 1.85;
    margin: 0 0 1.6rem 0;
}
.hero-badge-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.4rem; }
.hero-badge {
    font-size: 0.75rem;
    font-weight: 600;
    color: #374151;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 4px 10px;
}

/* ── Stats grid (right side of hero) ── */
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.8rem;
    height: 100%;
}
.stat-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.2rem 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.stat-box.accent-blue  { background: #eef3f8; border-color: #c5d8ea; }
.stat-box.accent-orange{ background: #fff4ef; border-color: #fcd5c0; }
.stat-box.accent-green { background: #edfaf3; border-color: #b9e8cc; }
.stat-box.accent-purple{ background: #f5f0fc; border-color: #d6c5f0; }
.stat-box-num {
    font-size: 2rem;
    font-weight: 800;
    color: #111827;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-box-lbl {
    font-size: 0.77rem;
    color: #6b7280;
    line-height: 1.4;
}

/* ── Why strip ── */
.why-strip {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 1.6rem 1.4rem;
}
.why-icon { font-size: 1.6rem; margin-bottom: 0.5rem; }
.why-title { font-size: 0.92rem; font-weight: 700; color: #111827; margin-bottom: 0.35rem; }
.why-desc  { font-size: 0.83rem; color: #6b7280; line-height: 1.65; }
.why-hl    { font-weight: 700; color: #ff6e40; }

/* ── Section label ── */
.sec-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #9ca3af;
    display: block;
    margin-bottom: 1rem;
}

/* ── Persona cards ── */
.p-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1.4rem;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.p-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #1e3d59;
    border-radius: 14px 14px 0 0;
}
.p-card.orange::before { background: #ff6e40; }
.p-card.green::before  { background: #27ae60; }
.p-card-icon  { font-size: 1.7rem; margin-bottom: 0.7rem; }
.p-card-title { font-weight: 700; font-size: 1rem; color: #111827; margin-bottom: 0.5rem; }
.p-card-desc  { font-size: 0.84rem; color: #6b7280; line-height: 1.7; margin-bottom: 1.1rem; }
.p-card-link  {
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 700;
    color: #1e3d59;
    background: #eef3f8;
    padding: 5px 12px;
    border-radius: 6px;
    letter-spacing: 0.3px;
}
.p-card.orange .p-card-link { color: #c94e20; background: #fff4ef; }
.p-card.green  .p-card-link { color: #1a7a42; background: #edfaf3; }

/* ── Steps horizontal ── */
.steps-outer {
    display: flex;
    gap: 0;
    position: relative;
}
.step-item {
    flex: 1;
    padding: 1.3rem 1.2rem;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-right: none;
    position: relative;
}
.step-item:first-child { border-radius: 12px 0 0 12px; }
.step-item:last-child  { border-right: 1px solid #e5e7eb; border-radius: 0 12px 12px 0; }
.step-num-pill {
    display: inline-block;
    width: 28px; height: 28px;
    border-radius: 50%;
    background: #111827;
    color: #fff;
    font-size: 0.78rem;
    font-weight: 800;
    text-align: center;
    line-height: 28px;
    margin-bottom: 0.8rem;
}
.step-title { font-weight: 700; font-size: 0.9rem; color: #111827; margin-bottom: 0.3rem; }
.step-desc  { font-size: 0.82rem; color: #6b7280; line-height: 1.6; }
.step-arrow {
    position: absolute;
    right: -10px; top: 50%;
    transform: translateY(-50%);
    width: 20px; height: 20px;
    background: #fff;
    border-top: 1px solid #e5e7eb;
    border-right: 1px solid #e5e7eb;
    transform: translateY(-50%) rotate(45deg);
    z-index: 1;
}

/* ── Footer ── */
.footer {
    margin-top: 2rem;
    padding-top: 1.2rem;
    border-top: 1px solid #f3f4f6;
    font-size: 0.74rem;
    color: #d1d5db;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HERO — 2 columns: text left | stats grid right
# ═══════════════════════════════════════════════════════════
col_hero, col_stats = st.columns([1.15, 1], gap="large")

with col_hero:
    st.markdown('<span class="eyebrow">Data-Driven Tourism Platform</span>', unsafe_allow_html=True)
    st.markdown(
        "<h1 class='hero-title'>ยกระดับท่องเที่ยวไทย<br>ด้วย <em>ข้อมูลจริง&nbsp;+&nbsp;AI</em></h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='hero-sub'>"
        "แพลตฟอร์มวิเคราะห์การท่องเที่ยว 77 จังหวัด เปลี่ยนข้อมูลดิบเป็น Actionable Insights "
        "พร้อม AI ช่วยวางแผนทริป กลยุทธ์ผู้ประกอบการ และข้อเสนอเชิงนโยบาย "
        "— ขับเคลื่อนด้วย <strong>Gemma 4</strong>"
        "</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-badge-row">'
        '<span class="hero-badge">📊 Market Analysis</span>'
        '<span class="hero-badge">🗄️ Tourism Database</span>'
        '<span class="hero-badge">🤖 CitySmart Planner</span>'
        '</div>',
        unsafe_allow_html=True
    )

with col_stats:
    st.markdown(
        '<div class="stat-grid">'

        '<div class="stat-box accent-blue">'
        '<div class="stat-box-num">77</div>'
        '<div class="stat-box-lbl">จังหวัดทั่วประเทศไทย<br>ครบทุกภูมิภาค</div>'
        '</div>'

        '<div class="stat-box accent-orange">'
        '<div class="stat-box-num">55</div>'
        '<div class="stat-box-lbl">เมืองรองที่รอการค้นพบ<br>ศักยภาพสูงแต่ยังซ่อนอยู่</div>'
        '</div>'

        '<div class="stat-box accent-green">'
        '<div class="stat-box-num">3 ปี</div>'
        '<div class="stat-box-lbl">ข้อมูลสถิติครบถ้วน<br>ปี 2566–2568</div>'
        '</div>'

        '<div class="stat-box accent-purple">'
        '<div class="stat-box-num">39</div>'
        '<div class="stat-box-lbl">เทศกาลสำคัญ<br>ทั่วประเทศในระบบ</div>'
        '</div>'

        '</div>',
        unsafe_allow_html=True
    )

st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# WHY SECONDARY CITIES — 3 pillars in gray strip
# ═══════════════════════════════════════════════════════════
st.markdown('<span class="sec-label">ทำไมต้องเมืองรอง</span>', unsafe_allow_html=True)

w1, w2, w3 = st.columns(3, gap="medium")
why_items = [
    ("🏔️", "ศักยภาพที่ซ่อนอยู่",
     "เมืองรองมีวัฒนธรรม ธรรมชาติ และอาหารท้องถิ่นที่ไม่แพ้เมืองหลัก "
     "แต่ยังไม่ถูกนำเสนอในวงกว้าง"),
    ("📉", "ช่องว่างรายได้สูงถึง 4–6 เท่า",
     "รายได้จากการท่องเที่ยวของเมืองรองยังต่ำกว่าเมืองหลักมาก "
     "ทั้งที่มีนักท่องเที่ยวกลุ่มใหม่พร้อมสำรวจ"),
    ("🔑", "โอกาสที่รอการปลดล็อก",
     "ด้วยข้อมูลที่ถูกต้องและ AI ที่เข้าใจบริบท "
     "เมืองรองทุกแห่งสามารถมีเรื่องราวที่ดึงดูดใจได้"),
]
for col, (icon, title, desc) in zip([w1, w2, w3], why_items):
    with col:
        st.markdown(
            f'<div class="why-strip">'
            f'<div class="why-icon">{icon}</div>'
            f'<div class="why-title">{title}</div>'
            f'<div class="why-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PERSONA CARDS — 3 columns
# ═══════════════════════════════════════════════════════════
st.markdown('<span class="sec-label">ออกแบบมาสำหรับทุกกลุ่ม</span>', unsafe_allow_html=True)

p1, p2, p3 = st.columns(3, gap="medium")
personas = [
    ("", "✈️", "นักท่องเที่ยว",
     "วางแผนทริป 3 วัน 2 คืน ค้นพบเมืองรองที่ซ่อนอยู่ พร้อมแนะนำ route และงบประมาณที่เหมาะกับคุณ",
     "→ CitySmart Planner"),
    ("orange", "🏪", "ผู้ประกอบการ",
     "รับกลยุทธ์การตลาดและโปรโมชั่นที่สอดคล้องกับเทศกาลและข้อมูลตลาดจริงของจังหวัดคุณ",
     "→ CitySmart Planner"),
    ("green", "🏛️", "ภาครัฐ / นักวิจัย",
     "วิเคราะห์ช่องว่างรายได้ High-Low Season และรับข้อเสนอนโยบายเพื่อกระตุ้นเศรษฐกิจท้องถิ่น",
     "→ Market Analysis"),
]
for col, (cls, icon, title, desc, link) in zip([p1, p2, p3], personas):
    with col:
        st.markdown(
            f'<div class="p-card {cls}">'
            f'<div class="p-card-icon">{icon}</div>'
            f'<div class="p-card-title">{title}</div>'
            f'<div class="p-card-desc">{desc}</div>'
            f'<span class="p-card-link">{link}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HOW TO — horizontal steps + callout side by side
# ═══════════════════════════════════════════════════════════
col_steps, col_note = st.columns([1.7, 1], gap="large")

with col_steps:
    st.markdown('<span class="sec-label">เริ่มต้นใช้งาน</span>', unsafe_allow_html=True)
    st.markdown(
        '<div class="steps-outer">'

        '<div class="step-item">'
        '<div class="step-num-pill">1</div>'
        '<div class="step-title">Market Analysis</div>'
        '<div class="step-desc">ดูเทรนด์ ช่องว่างรายได้ และจังหวัดที่น่าสนใจจากข้อมูลจริง</div>'
        '<div class="step-arrow"></div>'
        '</div>'

        '<div class="step-item">'
        '<div class="step-num-pill">2</div>'
        '<div class="step-title">Tourism Database</div>'
        '<div class="step-desc">เช็กปฏิทินเทศกาลและฐานข้อมูลสถานที่ท่องเที่ยวทั่วประเทศ</div>'
        '<div class="step-arrow"></div>'
        '</div>'

        '<div class="step-item">'
        '<div class="step-num-pill">3</div>'
        '<div class="step-title">CitySmart Planner</div>'
        '<div class="step-desc">ให้ Gemma 4 ช่วยวางแผนทริป กลยุทธ์ หรือนโยบายที่ปรับแต่งให้คุณ</div>'
        '</div>'

        '</div>',
        unsafe_allow_html=True
    )

with col_note:
    st.markdown('<span class="sec-label">หมายเหตุสำคัญ</span>', unsafe_allow_html=True)
    st.markdown(
        '<div style="background:#fff8f5;border:1px solid #fcd5c0;border-left:3px solid #ff6e40;'
        'border-radius:0 12px 12px 0;padding:1.3rem 1.3rem;">'
        '<p style="margin:0 0 0.6rem 0;font-size:0.85rem;font-weight:700;color:#c94e20;">📌 Data Source</p>'
        '<p style="margin:0;font-size:0.83rem;color:#374151;line-height:1.75;">'
        'ข้อมูลทั้งหมดมาจาก <strong>กระทรวงการท่องเที่ยวและกีฬา</strong> '
        'ปี 2566–2568 และ AI ขับเคลื่อนโดย <strong>Gemma 4 (gemma-4-31b-it)</strong> '
        'เพื่อการวิเคราะห์เชิงลึกที่เข้าใจบริบทไทย'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown(
    '<div class="footer">'
    'Gemma City-Smart Strategist &nbsp;·&nbsp; Powered by Gemma 4 (gemma-4-31b-it) '
    '&nbsp;·&nbsp; ข้อมูล: กระทรวงการท่องเที่ยวและกีฬา 2566–2568 '
    '&nbsp;·&nbsp; พัฒนาโดยทีม Gemma Tourism Lab'
    '</div>',
    unsafe_allow_html=True
)
