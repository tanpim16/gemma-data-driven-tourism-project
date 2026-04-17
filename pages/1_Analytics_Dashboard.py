import streamlit as st
import pandas as pd

# 1. ต้อง import ก่อนเสมอ
st.set_page_config(page_title="Analytics Dashboard")

# 2. ฟังก์ชันโหลด Data (ตรวจสอบให้แน่ใจว่าไฟล์อยู่ในโฟลเดอร์ data/)
@st.cache_data
def load_data():
    # เปลี่ยนชื่อไฟล์ให้ตรงกับที่คุณมีในโฟลเดอร์ data
    return pd.read_excel("data/Thailand_Festival_Master.xlsx")

try:
    df = load_data()
    
    st.title("📊 Tourism & Festival Analytics")

    # 3. ตอนนี้จะเรียกใช้ st.sidebar ได้แล้ว
    selected = st.sidebar.selectbox("เลือกจังหวัดที่สนใจ", df['Province_ID'].unique())
    
    # อัปเดตค่าไปยัง Session State เพื่อส่งต่อให้หน้าอื่น
    st.session_state['selected_province'] = selected
    
    # Filter ข้อมูลตามจังหวัดที่เลือก
    filtered_df = df[df['Province_ID'] == selected]
    
    st.write(f"### เทศกาลในจังหวัด {selected}")
    st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
    st.info("ตรวจสอบว่าไฟล์ Excel อยู่ในโฟลเดอร์ data/ หรือยัง?")