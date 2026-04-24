import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config for a wide layout
st.set_page_config(page_title="การวิเคราะห์และฐานข้อมูลการท่องเที่ยว (Tourism Analysis and Database)", layout="wide")

st.title("🇹🇭 📊 ฐานข้อมูลและการวิเคราะห์การท่องเที่ยว (Tourism Database & Time Series Analysis)")

st.write("""
เทศกาลและงานประเพณีถือเป็นเครื่องมือเชิงยุทธศาสตร์ที่ทรงพลังในการกระตุ้นดัชนีการท่องเที่ยวของประเทศไทย โดยทำหน้าที่เป็นแรงดึงดูดสำคัญที่ดึงมวลชนทั้งชาวไทยและต่างชาติให้เข้าสู่พื้นที่เป้าหมายตามช่วงเวลาต่าง ๆ  งานประเพณีระดับโลกในประเทศไทย เช่น สงกรานต์และลอยกระทง ไม่เพียงแต่สร้างภาพลักษณ์ที่ดีให้กับประเทศไทย แต่ยังก่อให้เกิดการใช้จ่ายหมุนเวียนในระบบนิเวศการท่องเที่ยวอย่างครบวงจร ตั้งแต่ธุรกิจที่พัก ร้านอาหาร คมนาคม ไปจนถึงบริการสันทนาการต่าง ๆ ส่งผลให้เกิดการทวีคูณของรายได้ทั้งในระดับฐานรากและระดับมหภาค

นอกจากนี้ เทศกาลยังเป็นเครื่องมือสำคัญในการ บริหารจัดการอุปสงค์ เพื่อลดความเหลื่อมล้ำทางรายได้โดยการกระตุ้นการเดินทางในช่วงนอกฤดูกาลท่องเที่ยวและผลักดันการกระจายตัวของนักท่องเที่ยวสู่เมืองรองและชุมชนท้องถิ่น อย่างเป็นรูปธรรม ในขณะเดียวกันเทศกาลยังเป็นโอกาสในการยกระดับทุนทางวัฒนธรรม เช่น งานหัตถศิลป์และอาหารพื้นถิ่นให้กลายเป็นสินค้าและบริการที่มีมูลค่าสูงซึ่งเป็นการสร้างโมเดลรายได้ที่ยั่งยืนและเข้มแข็งให้กับชุมชนอย่างแท้จริง
""")

# 1. Load the data 
@st.cache_data
def load_data_final():
    df = pd.read_csv('data/master_tourism_analysis.csv')
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-01')
    
    # ลบช่องว่างในชื่อเดือน
    df['Month'] = df['Month'].astype(str).str.strip()
    
    # ทำความสะอาดคอลัมน์ที่เป็นตัวเลขทั้งหมด (ลบเครื่องหมาย , และเว้นวรรค)
    numeric_cols = ['total_revenue', 'total_guests', 'total_visitors']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

@st.cache_data
def load_festival_final():
    df_festival = pd.read_csv('data/Thailand_Festival_With_Events.csv')
    df_festival['Month'] = df_festival['Month'].astype(str).str.strip()
    return df_festival

df = load_data_final()
df_festival = load_festival_final()

month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_names_th = {
    'Jan': 'มกราคม', 'Feb': 'กุมภาพันธ์', 'Mar': 'มีนาคม', 'Apr': 'เมษายน',
    'May': 'พฤษภาคม', 'Jun': 'มิถุนายน', 'Jul': 'กรกฎาคม', 'Aug': 'สิงหาคม',
    'Sep': 'กันยายน', 'Oct': 'ตุลาคม', 'Nov': 'พฤศจิกายน', 'Dec': 'ธันวาคม'
}

# ============================================================================
# DATA PREPARATION: Map English Names to Thai (Provinces & Regions)
# ============================================================================
province_th_map = {
    'Bangkok': 'กรุงเทพมหานคร', 'Bangkok Metropolis': 'กรุงเทพมหานคร', 'Chiang Mai': 'เชียงใหม่', 'Phuket': 'ภูเก็ต',
    'Pattaya': 'พัทยา', 'Krabi': 'กระบี่', 'Hua Hin': 'หัวหิน', 'Chiang Rai': 'เชียงราย', 
    'Phang Nga': 'พังงา', 'Phangnga': 'พังงา', 'Phang-nga': 'พังงา',
    'Bueng Kan': 'บึงกาฬ', 'Bungkan': 'บึงกาฬ', 'Buengkan': 'บึงกาฬ', 'Bueng-kan': 'บึงกาฬ',
    'Koh Samui': 'เกาะสมุย', 'Ayutthaya': 'พระนครศรีอยุธยา', 'Phra Nakhon Si Ayutthaya': 'พระนครศรีอยุธยา',
    'Kanchanaburi': 'กาญจนบุรี', 'Nakhon Ratchasima': 'นครราชสีมา', 'Ubon Ratchathani': 'อุบลราชธานี',
    'Surat Thani': 'สุราษฎร์ธานี', 'Nakhon Si Thammarat': 'นครศรีธรรมราช', 'Songkhla': 'สงขลา', 'Trang': 'ตรัง',
    'Satun': 'สตูล', 'Yala': 'ยะลา', 'Narathiwat': 'นราธิวาส', 'Pattani': 'ปัตตานี', 'Phatthalung': 'พัทลุง',
    'Chumphon': 'ชุมพร', 'Ranong': 'ระนอง', 'Prachuap Khiri Khan': 'ประจวบคีรีขันธ์', 'Phetchaburi': 'เพชรบุรี',
    'Ratchaburi': 'ราชบุรี', 'Samut Prakan': 'สมุทรปราการ', 'Samut Sakhon': 'สมุทรสาคร', 'Samut Songkhram': 'สมุทรสงคราม',
    'Nakhon Pathom': 'นครปฐม', 'Pathum Thani': 'ปทุมธานี', 'Nonthaburi': 'นนทบุรี', 'Saraburi': 'สระบุรี',
    'Lop Buri': 'ลพบุรี', 'Sing Buri': 'สิงห์บุรี', 'Ang Thong': 'อ่างทอง', 'Chai Nat': 'ชัยนาท', 'Suphan Buri': 'สุพรรณบุรี',
    'Nakhon Nayok': 'นครนายก', 'Prachin Buri': 'ปราจีนบุรี', 'Sa Kaeo': 'สระแก้ว', 'Chachoengsao': 'ฉะเชิงเทรา',
    'Chon Buri': 'ชลบุรี', 'Rayong': 'ระยอง', 'Chanthaburi': 'จันทบุรี', 'Trat': 'ตราด', 'Buri Ram': 'บุรีรัมย์',
    'Surin': 'สุรินทร์', 'Si Sa Ket': 'ศรีสะเกษ', 'Yasothon': 'ยโสธร', 'Chaiyaphum': 'ชัยภูมิ', 'Amnat Charoen': 'อำนาจเจริญ',
    'Nong Bua Lam Phu': 'หนองบัวลำภู', 'Khon Kaen': 'ขอนแก่น', 'Udon Thani': 'อุดรธานี', 'Loei': 'เลย',
    'Nong Khai': 'หนองคาย', 'Sakon Nakhon': 'สกลนคร', 'Nakhon Phanom': 'นครพนม', 'Mukdahan': 'มุกดาหาร',
    'Kalasin': 'กาฬสินธุ์', 'Roi Et': 'ร้อยเอ็ด', 'Maha Sarakham': 'มหาสารคาม', 'Lamphun': 'ลำพูน', 'Lampang': 'ลำปาง',
    'Uttaradit': 'อุตรดิตถ์', 'Phrae': 'แพร่', 'Nan': 'น่าน', 'Phayao': 'พะเยา', 'Mae Hong Son': 'แม่ฮ่องสอน',
    'Tak': 'ตาก', 'Kamphaeng Phet': 'กำแพงเพชร', 'Sukhothai': 'สุโขทัย', 'Phitsanulok': 'พิษณุโลก',
    'Phichit': 'พิจิตร', 'Phetchabun': 'เพชรบูรณ์', 'Nakhon Sawan': 'นครสวรรค์', 'Uthai Thani': 'อุทัยธานี'
}

df['ProvinceEN'] = df['ProvinceEN'].astype(str).str.strip()
df['ProvinceTH'] = df['ProvinceEN'].map(lambda x: province_th_map.get(x, x))

festival_months = set(df_festival['Month'].dropna().astype(str).str.strip().tolist())

# ============================================================================
# SECTION 1: Festival Impact Summary Dashboard 
# ============================================================================

st.header("📌 ส่วนที่ 1: วิเคราะห์ผลกระทบเทศกาลต่อรายได้")
st.write("เปรียบเทียบภาพรวมรายได้ระหว่างเดือนที่มีเทศกาลกับเดือนที่ไม่มีเทศกาลทั่วทุกจังหวัดในประเทศ แยกตามปี (หน่วย: ล้านล้านบาท)")

df_sec1 = df.copy()
df_sec1['Has_Festival'] = df_sec1['Month'].isin(festival_months)
years_sec1 = sorted(df_sec1['Year'].dropna().unique().tolist())

pastel_colors = ['#FFE4E1', '#E6E6FA', '#F0FFF0', '#FFF0F5', '#F0F8FF']

if len(years_sec1) > 0:
    cols = st.columns(len(years_sec1))
    
    for i, year in enumerate(years_sec1):
        year_data = df_sec1[df_sec1['Year'] == year]
        
        total_fest_trillion = year_data[year_data['Has_Festival']]['total_revenue'].sum() / 1000000.0
        total_non_fest_trillion = year_data[~year_data['Has_Festival']]['total_revenue'].sum() / 1000000.0
        
        inc_pct = ((total_fest_trillion - total_non_fest_trillion) / total_non_fest_trillion * 100) if total_non_fest_trillion > 0 else 0
        bg_color = pastel_colors[i % len(pastel_colors)]
        
        with cols[i]:
            trend_color = "#228B22" if inc_pct >= 0 else "#B22222"
            trend_icon = "📈 +" if inc_pct >= 0 else "📉 "
            
            html_card = f"""
            <div style="background-color: {bg_color}; padding: 20px; border-radius: 15px; border: 1px solid #eaeaea; box-shadow: 2px 4px 10px rgba(0,0,0,0.05); height: 100%;">
                <h3 style="color: #333; margin-top: 0; text-align: center;">📅 ปี {int(year)}</h3>
                <hr style="border-top: 1px solid #ddd; margin: 10px 0;">
                <p style="color: #555; font-size: 14px; margin-bottom: 2px;">รายได้เดือนมีเทศกาล</p>
                <h2 style="color: #00008B; margin-top: 0; margin-bottom: 5px; font-size: 26px;">
                    {total_fest_trillion:,.2f} <span style="font-size: 16px; color: #444;">ล้านล้านบาท</span>
                </h2>
                <p style="color: {trend_color}; font-weight: bold; font-size: 16px; margin-top: 0;">
                    {trend_icon}{inc_pct:,.1f}%
                </p>
                <p style="color: #555; font-size: 14px; margin-bottom: 2px; margin-top: 15px;">รายได้เดือนไม่มีเทศกาล</p>
                <h3 style="color: #444; margin-top: 0; font-size: 20px;">
                    {total_non_fest_trillion:,.2f} <span style="font-size: 14px; color: #555;">ล้านล้านบาท</span>
                </h3>
            </div>
            """.strip()
            
            st.html(html_card)
else:
    st.info("ไม่มีข้อมูลสำหรับวิเคราะห์ผลกระทบเทศกาล")

st.divider()

# ============================================================================
# SECTION 2: Revenue by Province Chart
# ============================================================================

st.header("📌 ส่วนที่ 2: เจาะลึกรายละเอียดรายได้ระดับจังหวัด")

available_provinces = sorted(df['ProvinceTH'].dropna().unique().tolist())

selected_province_name = st.selectbox(
    "🔍 ค้นหาและเลือกจังหวัด (Select Province)",
    options=available_provinces,
    key="province_selector"
)

if selected_province_name:
    st.subheader(f"🏢 ข้อมูลสถิติของจังหวัด: {selected_province_name}")

    province_yearly = df[df['ProvinceTH'] == selected_province_name].groupby('Year')['total_revenue'].sum().reset_index()
    province_yearly['total_revenue'] = province_yearly['total_revenue'].astype(float)

    st.write("💰 **สรุปรายได้ตามปี (Annual Revenue Summary)**")
    
    years = province_yearly['Year'].tolist()
    revenues = province_yearly['total_revenue'].tolist()
    
    if len(years) > 0:
        metric_cols = st.columns(len(years))
        for i, col in enumerate(metric_cols):
            with col:
                st.metric(
                    label=f"ปี {int(years[i])}", 
                    value=f"{revenues[i]:,.2f} ล้านบาท"
                )
    else:
        st.info("ไม่มีข้อมูลรายได้สำหรับจังหวัดนี้")

    available_years = sorted(province_yearly['Year'].tolist())
    selected_chart_year = st.selectbox(
        "📅 เลือกปีสำหรับการแสดงผลกราฟ",
        options=available_years,
        index=len(available_years) - 1 if available_years else 0,
        key="province_chart_year"
    )

    province_monthly_data = df[(df['ProvinceTH'] == selected_province_name) & (df['Year'] == selected_chart_year)].copy()
    province_monthly_data['Has_Festival'] = province_monthly_data['Month'].isin(festival_months)

    festival_col = 'Festival_Name_TH' if 'Festival_Name_TH' in df_festival.columns else 'Festival_Name_EN'

    chart_data = []
    for month in month_order:
        month_data = province_monthly_data[province_monthly_data['Month'] == month]
        if len(month_data) > 0:
            revenue = month_data['total_revenue'].iloc[0]
            has_festival = month_data['Has_Festival'].iloc[0]
        else:
            revenue = 0
            has_festival = False

        festival_names = "ไม่มี"
        if has_festival:
            fests = df_festival[df_festival['Month'] == month][festival_col].dropna().tolist()
            unique_fests = list(dict.fromkeys(fests))
            festival_names = "<br>".join(unique_fests) if unique_fests else "มีเทศกาล"

        chart_data.append({
            'Month': month_names_th[month],
            'Revenue': revenue,
            'Festival_Status': 'มีเทศกาล' if has_festival else 'ไม่มีเทศกาล',
            'Festivals': festival_names
        })

    chart_df = pd.DataFrame(chart_data)

    fig_monthly = px.bar(
        chart_df,
        x='Month',
        y='Revenue',
        color='Festival_Status',
        hover_data={'Festivals': True, 'Festival_Status': False},
        color_discrete_map={'มีเทศกาล': '#00008B', 'ไม่มีเทศกาล': '#87CEFA'}, 
        category_orders={'Month': [month_names_th[m] for m in month_order]},
        title=f'รายได้รายเดือน - {selected_province_name} ({int(selected_chart_year)})',
        labels={
            'Revenue': 'รายได้ (ล้านบาท)',
            'Month': 'เดือน',
            'Festival_Status': 'สถานะ',
            'Festivals': 'เทศกาล'
        }
    )

    fig_monthly.update_traces(
        hovertemplate="<b>เดือน:</b> %{x}<br><b>รายได้: %{y:,.2f} ล้านบาท</b><br><b>เทศกาล:</b><br>%{customdata[0]}<extra></extra>",
        texttemplate='%{y:,.1f}', 
        textposition='outside'
    )

    fig_monthly.update_layout(
        xaxis_title='เดือน',
        yaxis_title='รายได้ (ล้านบาท)',
        showlegend=True,
        height=500,
        uniformtext_minsize=8, 
        uniformtext_mode='hide',
        margin=dict(t=50, l=25, r=25, b=25)
    )

    st.plotly_chart(fig_monthly, use_container_width=True)

st.divider()

# ============================================================================
# SECTION 3: Province Revenue Comparison & Festival Impact (MULTIPLE YEARS & PROVINCES)
# ============================================================================

st.header("📌 ส่วนที่ 3: เปรียบเทียบรายได้ระดับจังหวัดและผลกระทบเทศกาล")
st.write("เลือกเปรียบเทียบจังหวัดได้สูงสุด 5 จังหวัด และสามารถเลือกดูข้อมูลเปรียบเทียบแบบข้ามปีได้ (หน่วย: ล้านบาท)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 เลือกจังหวัด (สูงสุด 5 จังหวัด)")
    # ถอด max_selections ออกเพื่อป้องกันข้อความภาษาอังกฤษ แล้วดักด้วยโค้ดภาษาไทยแทน
    selected_provinces_multi = st.multiselect(
        "จังหวัด:", 
        options=available_provinces, 
        default=available_provinces[:2] if len(available_provinces) > 1 else available_provinces
    )

with col2:
    st.subheader("📅 เลือกปี (เลือกได้มากกว่า 1 ปี)")
    available_years = sorted(df['Year'].unique().tolist())
    selected_years_multi = st.multiselect(
        "ปีสำหรับการเปรียบเทียบ:", 
        options=available_years, 
        default=[available_years[-1]] 
    )

# เช็คว่าเลือกจังหวัดเกิน 5 จังหวัดหรือไม่
if len(selected_provinces_multi) > 5:
    st.warning("⚠️ คุณเลือกเกินจำนวนที่กำหนด! กรุณาเลือกเปรียบเทียบสูงสุดไม่เกิน 5 จังหวัด (ลบจังหวัดออกก่อนเพื่อดูข้อมูล)")
elif selected_provinces_multi and selected_years_multi:
    filtered_data = df[(df['ProvinceTH'].isin(selected_provinces_multi)) & (df['Year'].isin(selected_years_multi))].copy()
    
    prov_monthly = filtered_data.groupby(['ProvinceTH', 'Year', 'Month']).agg({
        'total_revenue': 'sum'
    }).reset_index()
    
    # บังคับเรียงเดือนตามปฏิทิน
    prov_monthly['Month'] = pd.Categorical(prov_monthly['Month'], categories=month_order, ordered=True)
    prov_monthly = prov_monthly.sort_values(['ProvinceTH', 'Year', 'Month'])
    
    prov_monthly['MonthTH'] = prov_monthly['Month'].map(month_names_th)
    prov_monthly['Province_Year'] = prov_monthly['ProvinceTH'] + ' (' + prov_monthly['Year'].astype(str) + ')'
    
    # กำหนดสถานะ มีเทศกาล/ไม่มีเทศกาล
    prov_monthly['Festival_Status'] = prov_monthly['Month'].apply(lambda x: 'มีเทศกาล' if x in festival_months else 'ไม่มีเทศกาล')

    # 🎨 กำหนด Color Palette 
    pink_palette = ['#FCE4EC', '#F8BBD0', '#F48FB1', '#F06292', '#EC407A', '#E91E63', '#D81B60', '#C2185B', '#AD1457', '#880E4F']
    purple_palette = ['#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#9C27B0', '#8E24AA', '#7B1FA2', '#6A1B9A', '#4A148C']
    green_palette = ['#004b23', '#006400', '#007200', '#008000', '#38b000', '#70e000', '#9ef01a', '#ccff33', '#e0ff4f', '#f4ff81']

    color_map = {}
    for p_idx, prov in enumerate(selected_provinces_multi):
        for yr in selected_years_multi:
            label = f"{prov} ({yr})"
            # ใช้ p_idx * 2 เพื่อให้สีต่างกันชัดเจนขึ้นเมื่อเลือกแค่ 5 จังหวัด
            if str(yr) == '2566':
                color_map[label] = pink_palette[(p_idx * 2) % 10]
            elif str(yr) == '2567':
                color_map[label] = purple_palette[(p_idx * 2) % 10]
            elif str(yr) == '2568':
                color_map[label] = green_palette[(p_idx * 2) % 10]
            else:
                color_map[label] = px.colors.qualitative.Plotly[p_idx % 10]

    fig_prov = px.line(prov_monthly, x='MonthTH', y='total_revenue', color='Province_Year',
                         title="แนวโน้มรายได้รายเดือนแยกตามจังหวัดและปี (คลิกที่ Legend เพื่อซ่อน/แสดง)",
                         markers=True, 
                         color_discrete_map=color_map, 
                         hover_data={'ProvinceTH': True, 'Festival_Status': True, 'MonthTH': False, 'Province_Year': False},
                         category_orders={'MonthTH': [month_names_th[m] for m in month_order]},
                         labels={'total_revenue': 'รายได้ (ล้านบาท)', 'MonthTH': 'เดือน', 'Province_Year': 'จังหวัด (ปี)'})
    
    # ปรับ Tooltip (Label) 3 บรรทัดเป๊ะๆ
    fig_prov.update_traces(
        hovertemplate="<b>ชื่อจังหวัด:</b> %{customdata[0]}<br><b>รายได้:</b> %{y:,.2f} ล้านบาท<br><b>สถานะ:</b> %{customdata[1]}<extra></extra>",
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    fig_prov.update_layout(
        xaxis_title='เดือน',
        yaxis_title='รายได้ (ล้านบาท)',
        legend_title='จังหวัด (ปี)',
        margin=dict(t=50, l=25, r=25, b=25),
        hovermode="x unified" 
    )

    st.plotly_chart(fig_prov, use_container_width=True)
elif len(selected_provinces_multi) == 0 or len(selected_years_multi) == 0:
    st.info("กรุณาเลือกจังหวัดและปีที่ต้องการเปรียบเทียบอย่างน้อย 1 รายการ")

st.divider()

# ============================================================================
# SECTION 4: Time Series Analysis
# ============================================================================

st.header("📌 ส่วนที่ 4: แนวโน้มการท่องเที่ยวตามเวลา (Time Series)")

metrics_map_th = {
    'total_revenue': 'รายได้รวม (Total Revenue)',
    'total_guests': 'จำนวนผู้เข้าพัก (Total Guests)',
    'total_visitors': 'จำนวนนักท่องเที่ยว (Total Visitors)'
}

metrics = df.select_dtypes(include=['number']).columns.tolist()
metrics = [m for m in metrics if m not in ['Year', 'Month', 'No', 'Price_Index', 'Latitude', 'Longitude']]
display_metrics = {m: metrics_map_th.get(m, m) for m in metrics}

st.write("⚙️ **เลือกตัวชี้วัดที่ต้องการวิเคราะห์:**")
selected_display_metric = st.selectbox("", options=list(display_metrics.values()), label_visibility="collapsed")
selected_metric = [k for k, v in display_metrics.items() if v == selected_display_metric][0]

if 'Date' in df.columns:
    ts_data = df.groupby('Date')[selected_metric].sum().reset_index()
    
    y_axis_label = f'{selected_display_metric} (ล้านบาท)' if 'revenue' in selected_metric.lower() else f'{selected_display_metric} (คน)'
    
    fig = px.line(ts_data, x='Date', y=selected_metric, 
                  title=f"แนวโน้มตามเวลา: {selected_display_metric}",
                  color_discrete_sequence=['#00008B'],
                  labels={
                      selected_metric: y_axis_label,
                      'Date': 'วันที่ (Date)'
                  })
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("ไม่พบคอลัมน์ 'Date' สำหรับการวิเคราะห์แนวโน้มตามเวลา")

