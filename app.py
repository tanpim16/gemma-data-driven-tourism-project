import streamlit as st

st.set_page_config(page_title="CitySmart | Introduction", page_icon="🏠")


# --- 🪄 Magic CSS: บีบช่องไฟให้ใกล้กันขึ้น ---
st.markdown("""
    <style>
        /* ลดช่องว่างด้านบนสุดของหน้า */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 0rem;
        }
        /* ลดช่องว่างระหว่าง Element ต่างๆ */
        .stVerticalBlock {
            gap: 0.8rem;
        }
        /* ปรับแต่งหัวข้อ */
        h2 { margin-bottom: 0px !important; }
        p { margin-bottom: 5px !important; }
        hr { margin-top: 10px !important; margin-bottom: 15px !important; }
    </style>
""", unsafe_allow_html=True)

# --- ส่วนหัว: กระชับพื้นที่ ---
st.markdown("<h2 style='text-align: center; color: #1E3D59;'>CitySmart</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #576574; font-size: 16px;'>ออกไปค้นหาเมืองไทยในมุมใหม่ๆ ที่คุณอาจไม่เคยเจอ</p>", unsafe_allow_html=True)

st.divider()

# --- ส่วนเนื้อหา: จัด Layout ให้ชิดกันมากขึ้น ---
col1, space, col2 = st.columns([1, 0.1, 1.5]) # ลด space ตรงกลางเหลือ 0.1

with col1:
    st.markdown("#### ✨ แพลนทริปง่ายๆ ใน 1 นาที")
    st.write("ไม่ว่าคุณจะอยากเช็คอินเมืองดัง หรือสงบกายในเมืองลับ เราช่วยจัดตารางเที่ยวให้ลงตัว พร้อมข้อมูลเทศกาลทั่วประเทศ ให้ทริปของคุณ 'พิเศษ' กว่าครั้งไหนๆ")
    
    st.markdown("#### 💡 อัพเกรดทริปของคุณ")
    st.info("ลองเลือกจุดหมายหลัก แล้วเราจะแอบแนะนำ 'พิกัดลับ' ข้างเคียงที่คุณอาจจะชอบเพิ่มเข้าไปให้!")

with col2:
    st.image("picture/PIC_Amazing TH.jpg", use_container_width=True)
    st.markdown("<p style='text-align: right; color: #95a5a6; font-size: 11px; margin-top: -10px;'>ขอขอบพระคุณรูปภาพจาก การท่องเที่ยวแห่งประเทศไทย</p>", unsafe_allow_html=True)

st.divider()

# --- ส่วนขั้นตอน: กระชับพื้นที่ช่วงล่าง ---
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("<p style='text-align: center; font-size: 14px;'>🔍 <b>ส่องข้อมูล</b><br>ดูเทรนด์ที่หน้า Explore</p>", unsafe_allow_html=True)

with c2:
    st.markdown("<p style='text-align: center; font-size: 14px;'>🤖 <b>ให้ AI ช่วยจัด</b><br>เลือกจังหวัดที่หน้า Advisor</p>", unsafe_allow_html=True)

with c3:
    st.markdown("<p style='text-align: center; font-size: 14px;'>📍 <b>ปรับแต่งตามใจ</b><br>เพิ่ม 'เมืองแนะนำ' ให้คูลกว่าเดิม</p>", unsafe_allow_html=True)

st.divider()
st.caption("CitySmart - สนุกกับการค้นหาเมืองไทยในแบบที่เป็นคุณ")