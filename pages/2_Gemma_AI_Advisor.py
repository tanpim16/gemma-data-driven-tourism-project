import streamlit as st
import google.generativeai as genai

# 1. เชื่อมต่อกับ API Key ที่เราเก็บไว้ในความลับ
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🤖 Gemma AI Strategy Consultant")

# 2. เลือกสมอง AI (ถ้าหา Gemma 4 ไม่เจอ ให้ใช้ Gemini 1.5 Flash ไปก่อนได้ครับ)
model = genai.GenerativeModel('gemma-4-31b-it')

# 3. ส่วนรับคำถามจาก User
user_question = st.text_input("ถามคำถามเกี่ยวกับกลยุทธ์เมืองรองที่นี่:")

if user_question:
    # 4. ส่งคำถามให้ AI และรับคำตอบ
    with st.spinner('Gemma กำลังประมวลผลกลยุทธ์ให้คุณ...'):
        response = model.generate_content(user_question)
        st.write("### คำแนะนำจาก AI:")
        st.write(response.text)