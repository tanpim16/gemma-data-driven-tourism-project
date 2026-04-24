import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CitySmart | Market Analysis", page_icon="📈")

# CSS บีบช่องไฟให้เหมือนหน้าแรก
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df_t = pd.read_csv('data/master_tourism_analysis.csv')
    df_f = pd.read_excel('data/Thailand_Festival_Master.xlsx')
    return df_t.dropna(subset=['ProvinceEN']), df_f

try:
    df_tour, df_fest = load_data()

    st.markdown("<h2 style='color: #1E3D59;'>Market Analysis</h2>", unsafe_allow_html=True)
    st.write("เจาะลึกสถิติการท่องเที่ยวทั่วไทย เพื่อค้นหาโอกาสใหม่ๆ ในทุกจังหวัด")

    # แยกพาร์ทด้วย Tabs เพื่อลดความแน่น
    tab_national, tab_province = st.tabs(["🌐 ภาพรวมประเทศไทย", "📍 ข้อมูลรายจังหวัด"])

    with tab_national:
        st.write("")
        c1, c2 = st.columns([1, 1.2])
        
        # คำนวณสรุปสัดส่วนเมือง
        summary = df_tour.groupby('City_type_EN').agg({'total_revenue':'mean', 'occupancy_rate':'mean'}).reset_index()

        with c1:
            st.markdown("#### ส่วนแบ่งรายได้")
            fig_p = px.pie(summary, values='total_revenue', names='City_type_EN', hole=0.6,
                          color_discrete_sequence=['#1E3D59', '#FF6E40'])
            fig_p.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_p, use_container_width=True)
            st.caption("สัดส่วนรายได้เฉลี่ยระหว่างเมืองหลัก (น้ำเงิน) และเมืองรอง (ส้ม)")

        with c2:
            st.markdown("#### อัตราการเข้าพักเฉลี่ย (%)")
            fig_b = px.bar(summary, x='City_type_EN', y='occupancy_rate', color='City_type_EN',
                          color_discrete_map={'Major City': '#1E3D59', 'Secondary City': '#FF6E40'},
                          text_auto='.1f')
            fig_b.update_layout(xaxis_title="", yaxis_title="", showlegend=False, margin=dict(t=20, b=0))
            st.plotly_chart(fig_b, use_container_width=True)

    with tab_province:
        st.write("")
        # ส่วนเลือกจังหวัดที่ดูสะอาด
        selected_province = st.selectbox("คุณกำลังสนใจจังหวัดไหน?", sorted(df_tour['ProvinceEN'].unique()))
        st.session_state['selected_province'] = selected_province
        
        p_df = df_tour[df_tour['ProvinceEN'] == selected_province].copy()
        # คำนวณรายได้จริง (คูณล้าน) หารจำนวนคน
        p_df['spend'] = (p_df['total_revenue'] * 1000000) / p_df['total_visitors'].replace(0,1)
        
        # Metric Card แบบเรียบง่าย
        m1, m2, m3 = st.columns(3)
        m1.metric("ยอดใช้จ่ายต่อหัว", f"{p_df['spend'].mean():,.0f} บาท")
        m2.metric("นักท่องเที่ยวเฉลี่ย/เดือน", f"{p_df['total_visitors'].mean():,.0f} คน")
        m3.metric("อัตราเข้าพักเฉลี่ย", f"{p_df['occupancy_rate'].mean():.1f}%")

        st.write("")
        # กราฟรายได้แบบ Bar บ่งบอกเทรนด์รายปี
        fig_rev = px.bar(p_df, x='Month', y='total_revenue', color='Year', barmode='group',
                         title=f"รายได้จากการท่องเที่ยวรายเดือน: {selected_province}",
                         color_discrete_sequence=px.colors.sequential.YlGnBu)
        fig_rev.update_layout(yaxis_title="ล้านบาท", xaxis_title="เดือน")
        st.plotly_chart(fig_rev, use_container_width=True)

        st.divider()
        
        # เทศกาลโชว์แบบ List เรียบๆ
        st.markdown(f"#### 📅 เทศกาลที่น่าสนใจใน {selected_province}")
        f_list = df_fest[df_fest['Province_ID'] == selected_province]
        if not f_list.empty:
            cols = st.columns(len(f_list) if len(f_list) <= 3 else 3)
            for i, (_, row) in enumerate(f_list.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""
                    **{row['Festival_Name_TH']}** 🗓️ เดือน {row['Month']}  
                    ⭐ Impact Score: {row['Economic_Impact']}/10
                    """)
        else:
            st.caption("ยังไม่มีข้อมูลเทศกาลในจังหวัดนี้")

except Exception as e:
    st.error(f"ไม่สามารถแสดงผลข้อมูลได้: {e}")