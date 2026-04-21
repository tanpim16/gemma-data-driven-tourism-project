import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้ากระดาษแบบ Wide
st.set_page_config(page_title="City Strategy Dashboard", layout="wide")

@st.cache_data
def load_data():
    # โหลดข้อมูลและจัดการเบื้องต้น
    df_tour = pd.read_csv('data/master_tourism_analysis.csv')
    df_fest = pd.read_excel('data/Thailand_Festival_Master.xlsx')
    df_tour = df_tour.dropna(subset=['ProvinceEN'])
    return df_tour, df_fest

try:
    df_tour, df_fest = load_data()

    st.title("🏙️ Strategic Tourism Dashboard")
    st.markdown("### การวิเคราะห์ข้อมูลเชิงลึกเมืองรอง (เฉลี่ย 3 ปี: 2566-2568)")
    st.divider()

    # --- ส่วนที่ 1: เปรียบเทียบเมืองหลัก vs เมืองรอง ---
    st.header("📊 National Level Comparison")
    
    # คำนวณรายได้เป็นล้านบาทเพื่อให้กราฟอ่านง่าย
    avg_data = df_tour.groupby('City_type_EN').agg({
        'total_revenue': 'mean',
        'occupancy_rate': 'mean'
    }).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ส่วนแบ่งรายได้เฉลี่ย (Market Share)")
        fig_pie = px.pie(avg_data, values='total_revenue', names='City_type_EN', 
                         hole=0.4, color_discrete_sequence=['#1F618D', '#5DADE2'])
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with c2:
        st.subheader("อัตราการเข้าพักเฉลี่ย (%)")
        fig_bar_comp = px.bar(avg_data, x='City_type_EN', y='occupancy_rate', 
                              color='City_type_EN', text_auto='.2f',
                              color_discrete_map={'Major City': '#1F618D', 'Secondary City': '#F39C12'})
        st.plotly_chart(fig_bar_comp, use_container_width=True)

    st.divider()

    # --- ส่วนที่ 2: เจาะลึกรายจังหวัด (Average 2566-2568) ---
    st.header("📍 Province Performance (3-Year Average)")
    
    all_provinces = sorted(df_tour['ProvinceEN'].unique())
    selected_province = st.selectbox("เลือกจังหวัดเป้าหมาย:", all_provinces)
    st.session_state['selected_province'] = selected_province

    # ดึงข้อมูลเฉพาะจังหวัด
    prov_df = df_tour[df_tour['ProvinceEN'] == selected_province].copy()

    # --- 🛠️ จุดที่แก้ไข: คำนวณยอดใช้จ่ายให้ถูกต้อง (Revenue x 1,000,000) ---
    # เราคูณ 1,000,000 เพราะในไฟล์ csv เก็บหน่วยเป็น "ล้านบาท"
    prov_df['actual_revenue_baht'] = prov_df['total_revenue'] * 1000000
    prov_df['spending_per_head'] = prov_df['actual_revenue_baht'] / prov_df['total_visitors'].replace(0, 1)

    # คำนวณค่าเฉลี่ย 3 ปี (หาร 3 ปี หรือเฉลี่ยจากข้อมูลทั้งหมดที่มี)
    avg_spending = prov_df['spending_per_head'].mean()
    avg_visitors_yearly = prov_df.groupby('Year')['total_visitors'].sum().mean()
    avg_occ = prov_df['occupancy_rate'].mean()

    # แสดงผล Metrics Card
    m1, m2, m3 = st.columns(3)
    m1.metric("ยอดใช้จ่ายต่อหัว (เฉลี่ย)", f"{avg_spending:,.2f} บาท")
    m2.metric("จำนวนนักท่องเที่ยว (เฉลี่ยต่อปี)", f"{avg_visitors_yearly:,.0f} คน")
    m3.metric("อัตราเข้าพักเฉลี่ย", f"{avg_occ:.2f}%")

    st.write("") 

    # กราฟแท่งรายปีแบบจัดกลุ่ม (อ่านง่ายกว่ากราฟเส้น)
    st.subheader("💰 เปรียบเทียบรายได้รายเดือน (รายได้หน่วย: ล้านบาท)")
    fig_bar_revenue = px.bar(prov_df, x='Month', y='total_revenue', color='Year',
                             barmode='group', 
                             title=f"Monthly Revenue Comparison (2566-2568): {selected_province}",
                             labels={'total_revenue': 'รายได้ (ล้านบาท)', 'Month': 'เดือน'},
                             color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_bar_revenue, use_container_width=True)

    st.divider()

    # --- ส่วนที่ 3: เทศกาลและการประเมิน Impact ---
    col_fest, col_info = st.columns([1.5, 1])

    with col_fest:
        st.subheader(f"📅 ไฮไลท์เทศกาลใน {selected_province}")
        fest_data = df_fest[df_fest['Province_ID'] == selected_province]
        if not fest_data.empty:
            for _, row in fest_data.iterrows():
                st.markdown(f"""
                <div style="background-color:#FBFCFC; padding:15px; border-radius:10px; border-left: 5px solid #F39C12; margin-bottom:12px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                    <h4 style="margin:0; color:#1F618D;">{row['Festival_Name_TH']}</h4>
                    <p style="margin:5px 0;">🗓️ เดือน: {row['Month']} | ⏱️ ระยะเวลา: {row['Duration_Days']} วัน</p>
                    <p style="margin:0;">🔥 <b>Economic Impact Score: {row['Economic_Impact']}/10</b></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีข้อมูลเทศกาลในฐานข้อมูล")

    with col_info:
        st.subheader("💡 นิยามระดับ 'ความแรง'")
        with st.expander("เกณฑ์การวัดผล (Stay & Wealth Impact)", expanded=True):
            st.write("""
            เราปรับเกณฑ์ใหม่ให้เน้น **Impact ต่อชุมชน** มากขึ้น:
            
            1. **Stay Conversion (การพักค้างคืน):** งานที่เปลี่ยนคน 'แค่แวะมา' ให้กลายเป็น 'คนพักค้างคืน' โดยวัดจากความสัมพันธ์กับค่า Occupancy Rate (งานที่จัดหลายวันและมีกิจกรรมกลางคืนจะได้คะแนนส่วนนี้สูง)
            
            2. **Local Wealth Retention:** วัดจากยอดใช้จ่ายเฉลี่ยต่อหัว (Spending per Head) หากงานมีสินค้าชุมชนหรืออาหารถิ่นที่โดดเด่น จะช่วยให้เงินหมุนเวียนในจังหวัดได้จริง
            
            3. **Seasonality Resilience:** ความสามารถในการดึงคนมาเที่ยวในช่วง Low Season (หน้าฝน) เพื่อให้ธุรกิจเมืองรองอยู่รอดได้ทั้งปี
            """)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")