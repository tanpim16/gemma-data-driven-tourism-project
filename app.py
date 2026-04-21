import streamlit as st

st.set_page_config(page_title="Gemma City-Smart Strategist", layout="wide")

st.title("🏙️ Gemma City-Smart Strategist")
st.markdown("### ยกระดับการท่องเที่ยวเมืองรองด้วยพลังของ Data & AI")

st.divider()

# ส่วนเนื้อหา Issues & Motivation 
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📌 ปัญหาและความท้าทาย (Issues)")
    st.write("""
    - **การกระจุกตัวของรายได้:** 80% ของรายได้ท่องเที่ยวไทยยังอยู่ที่เมืองหลัก
    - **ความยากในการวิเคราะห์:** ผู้ประกอบการท้องถิ่นเข้าถึงข้อมูล Insight ได้ยาก
    - **โอกาสที่หายไป:** เมืองรองมีเทศกาลที่น่าสนใจมากมาย แต่ขาดการวางแผนกลยุทธ์ที่แม่นยำ
    """)

with col2:
    st.info("""
    **เป้าหมายของโปรเจค:**
    เราใช้ **Gemma 4** ร่วมกับข้อมูลเทศกาล 39 แห่งทั่วประเทศ เพื่อสร้างเครื่องมือช่วยตัดสินใจให้กับนักท่องเที่ยวและภาครัฐ
    """)

st.divider()
st.write("👈 **กรุณาเลือกเมนูที่แถบด้านข้าง** เพื่อเริ่มวิเคราะห์ข้อมูลหรือคุยกับ AI")

# เซตค่าเริ่มต้นให้ Session State (ป้องกัน Error เวลาข้ามหน้า)
if 'selected_province' not in st.session_state:
    st.session_state['selected_province'] = 'Lampang'