import streamlit as st

# 1. การตั้งค่าหน้าเว็บ (Config)
st.set_page_config(
    page_title="Gemma-Insight | Smart Tourism Strategist",
    page_icon="🧭",
    layout="wide"
)

# 2. การจัดการ Session State (หัวใจของ Data-centric App)
# เราสร้างตัวแปรเก็บไว้ใน Session เพื่อให้หน้าอื่นดึงไปใช้ได้
if 'selected_province' not in st.session_state:
    st.session_state['selected_province'] = "All Thailand"

if 'selected_region' not in st.session_state:
    st.session_state['selected_region'] = "All Regions"

# 3. Sidebar Menu
st.sidebar.title("🧭 Navigation")
st.sidebar.info("Select a mode from the sidebar to begin your analysis.")

# 4. Main Content (Home Page)
st.title("🧭 Gemma-Insight: Smart-Event Strategist")
st.subheader("Leveraging AI to Empower Thailand's Secondary Cities")

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 🌟 About the Project
    Welcome to **Gemma-Insight**, a data-driven application designed to transform 
    how we approach tourism in Thailand's 55 secondary cities. 
    
    Our app helps stakeholders bridge the gap between complex tourism statistics 
    and actionable business strategies by using **Google's Gemma 4 AI**.
    
    ### 🚀 How it works:
    1. **Explore Analytics:** Go to the **Analytics Dashboard** to see trends, revenues, and festival impacts.
    2. **Get AI Insights:** Switch to **Gemma AI Advisor** to get personalized strategic recommendations based on the data you've filtered.
    """)

with col2:
    st.info("💡 **Quick Start**\n\nChoose a province in the Dashboard to update the AI's context automatically!")
    
    # แสดงสถานะปัจจุบัน (Data Context)
    st.write(f"**Current Context:** {st.session_state['selected_province']}")
    st.write(f"**Region:** {st.session_state['selected_region']}")

st.markdown("---")
st.caption("Developed for the Data Analytics and Data Science (DADS) Final Project.")